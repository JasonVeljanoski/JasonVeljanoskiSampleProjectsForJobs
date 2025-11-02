import json

from app import crud, models, schemas, utils
from app.models import workgroup
from app.schemas.enums import PrivacyEnum, StatusEnum
from app.schemas.user import Access
from app.utils import redis_helper
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from .base import RULE_SQL, CRUD_Base, Rule, Rules, add_date_filter


class Action(CRUD_Base[schemas.Action]):
    def get_basic_user_actions_page(
        self,
        db,
        user_id,
        page,
        count,
        sort_by=["priority", "status", "date_due"],
        sort_desc=[False, False, False],
        **filters,
    ):
        """
        BASIC USER PERMISSIONS
        ---------------------------
        A basic user can see:
            [1]. Actions that they belong to (owner, member, supervisor)
                    - these actions can have any privacy
            [2]. All PUBLIC actions
            [3]. All actions that are in a workgroup that I belong to
            [4]. Non-Archived actions only
        """
        member_query = (
            db.query(schemas.Action_Member_Association.id)
            .filter(schemas.Action_Member_Association.action_id == self.schema.id)
            .filter(schemas.Action_Member_Association.user_id == user_id)
        )

        # ------------------------------------------------
        # [3]. All actions that are in a workgroup that I belong to
        workgroup_member_query = (
            db.query(schemas.Workgroup_Member_Association.id)
            .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Member_Association.user_id == user_id)
        )
        workgroup_admin_query = (
            db.query(schemas.Workgroup_Admin_Association.id)
            .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Admin_Association.user_id == user_id)
        )
        my_workgroup_query = db.query(schemas.Workgroup).filter(
            or_(
                self.schema.owner_id == user_id,
                workgroup_member_query.exists(),
                workgroup_admin_query.exists(),
            )
        )
        workgroup_query = (
            db.query(schemas.Workgroup_Action_Association)
            .filter(
                schemas.Workgroup_Action_Association.workgroup_id
                == my_workgroup_query.subquery().c.id
            )
            .distinct()
        )
        # ------------------------------------------------

        query = (
            db.query(self.schema)
            # .filter(self.schema.is_archived.isnot(True))
            .filter(
                or_(
                    self.schema.owner_id == user_id,
                    self.schema.supervisor_id == user_id,
                    member_query.exists(),
                    workgroup_query.exists(),
                    self.schema.privacy == PrivacyEnum.PUBLIC,
                )
            )
        )

        # ------------------------------------------
        # todo - this code is copied from crud base. make wrapper function in crud base as it is used in multiple places. i tried, i failed. (it's late)

        # JW. 2022-11-20. Order by status, priority then date due
        if not sort_by:
            sort_by = ["priority", "status", "date_due"]
            sort_desc = [False, False, False]
        orders = []
        for by, desc in zip(sort_by, sort_desc):
            col = getattr(self.schema, by)
            if desc:
                col = col.desc()
            orders.append(col)

        orders.append(self.schema.id.desc())

        if orders:
            query = query.order_by(*orders)

        query = self.__add_filters__(db, query, filters)

        return dict(items=query.limit(count).offset((page - 1) * count).all(), count=query.count())

    def get_system_admin_actions_page(
        self,
        db,
        user_id,
        page,
        count,
        sort_by=["priority", "status", "date_due"],
        sort_desc=[False, False, False],
        **filters,
    ):
        """
        SYSTEM ADMIN PERMISSIONS
        ---------------------------
        A system admin can see:
            [1]. All actions with no restrictions (could change)
        """

        # JW. 2022-11-20. Order by status, priority then date due
        if not sort_by:
            sort_by = ["priority", "status", "date_due"]
            sort_desc = [False, False, False]

        return crud.action.get_page(db, page, count, sort_by, sort_desc, **filters)

    def get_action_titles(self, db, user):
        """
        Any user can see:
            [1]. Actions that they belong to (owner, member, supervisor)
                    - these actions can have any privacy
            [2]. All PUBLIC actions
            [3]. All actions that are in a workgroup that I belong to
            [4]. Non-Archived actions only
        """

        member_query = (
            db.query(schemas.Action_Member_Association.id)
            .filter(schemas.Action_Member_Association.action_id == self.schema.id)
            .filter(schemas.Action_Member_Association.user_id == user.id)
        )

        # ------------------------------------------------
        # [3]. All actions that are in a workgroup that I belong to
        workgroup_member_query = (
            db.query(schemas.Workgroup_Member_Association.id)
            .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Member_Association.user_id == user.id)
        )
        workgroup_admin_query = (
            db.query(schemas.Workgroup_Admin_Association.id)
            .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Admin_Association.user_id == user.id)
        )
        my_workgroup_query = db.query(schemas.Workgroup).filter(
            or_(
                self.schema.owner_id == user.id,
                workgroup_member_query.exists(),
                workgroup_admin_query.exists(),
            )
        )
        workgroup_query = (
            db.query(schemas.Workgroup_Action_Association)
            .filter(
                schemas.Workgroup_Action_Association.workgroup_id
                == my_workgroup_query.subquery().c.id
            )
            .distinct()
        )
        # ------------------------------------------------

        query = (
            db.query(self.schema)
            .filter(self.schema.is_archived.isnot(True))
            .filter(self.schema.type != "Teams")
            .filter(
                or_(
                    self.schema.owner_id == user.id,
                    self.schema.supervisor_id == user.id,
                    member_query.exists(),
                    workgroup_query.exists(),
                    self.schema.privacy == PrivacyEnum.PUBLIC
                )
            )
        )

        return query.all()

    def update_privacy(self, db, action_id, privacy):
        db.query(self.schema).filter(self.schema.id == action_id).update(
            {
                "privacy": privacy,
                "updated": utils.get_time_now(),
            }
        )
        db.commit()

    def __add_filters__(self, db, query, filters):

        # DEFINE JOINS HERE
        if "workgroup_ids" in filters:
            query = query.join(schemas.Workgroup_Action_Association)

        # ------------------------------------------------------------------------------------

        if "my_ace" in filters:
            user_id = filters["user"].id

            # HELPER QUERIES
            member_query = (
                db.query(schemas.Action_Member_Association.id)
                .filter(schemas.Action_Member_Association.action_id == self.schema.id)
                .filter(schemas.Action_Member_Association.user_id == user_id)
            )

            workcenters_query = [
                self.schema.work_center.contains(workcenter)
                for workcenter in filters["user"].work_centers or []
            ]
            flocs_query = [
                self.schema.functional_location.contains(floc)
                for floc in filters["user"].functional_locations or []
            ]

            # QUERY
            if workcenters_query and flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id == user_id,
                        member_query.exists(),
                        and_(
                            or_(*flocs_query),
                            or_(*workcenters_query),
                            or_(
                                self.schema.type == "SAP_Notification",
                                self.schema.type == "SAP_Work_Order",
                            ),
                        ),
                        and_(
                            or_(*flocs_query),
                            self.schema.type == "AHM",
                        ),
                    )
                )
            elif not flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id == user_id,
                        member_query.exists(),
                        # and_(
                        #     or_(*flocs_query),
                        #     or_(*workcenters_query),
                        #     or_(
                        #         self.schema.type == "SAP_Notification",
                        #         self.schema.type == "SAP_Work_Order",
                        #     ),
                        # ),
                        # and_(
                        #     or_(*flocs_query),
                        #     self.schema.type == "AHM",
                        # ),
                    )
                )
            elif flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id == user_id,
                        member_query.exists(),
                        # and_(
                        #     or_(*flocs_query),
                        #     or_(*workcenters_query),
                        #     or_(
                        #         self.schema.type == "SAP_Notification",
                        #         self.schema.type == "SAP_Work_Order",
                        #     ),
                        # ),
                        and_(
                            or_(*flocs_query),
                            self.schema.type == "AHM",
                        ),
                    )
                )

            del filters["my_ace"]

        # ------------------------------------------------------------------------------------

        if "my_team" in filters:
            redis_db = redis_helper.Redis_Client()
            user_teams = json.loads(redis_db.get("user_teams"))
            user = filters["user"]

            if str(user.id) in user_teams:

                me_and_my_team = user_teams[str(user.id)]
                me_and_my_team.append(
                    {
                        "user_id": user.id,
                        "email": user.email,
                        "functional_locations": user.functional_locations,
                        "work_centers": user.work_centers,
                    }
                )
            else:
                me_and_my_team = [
                    {
                        "user_id": user.id,
                        "email": user.email,
                        "functional_locations": user.functional_locations,
                        "work_centers": user.work_centers,
                    }
                ]

            # user ids
            user_ids = [user["user_id"] for user in me_and_my_team]

            # HELPER QUERIES
            member_query = (
                db.query(schemas.Action_Member_Association.id)
                .filter(schemas.Action_Member_Association.action_id == self.schema.id)
                .filter(schemas.Action_Member_Association.user_id.in_(user_ids))
            )

            workcenters_query = []
            flocs_query = []
            for user in me_and_my_team:
                workcenters_query = workcenters_query + [
                    self.schema.work_center.contains(workcenter)
                    for workcenter in user["work_centers"] or []
                    if user["work_centers"]
                ]
                flocs_query = flocs_query + [
                    self.schema.functional_location.contains(floc)
                    for floc in user["functional_locations"] or []
                    if user["functional_locations"]
                ]

            # QUERY
            if workcenters_query and flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id.in_(user_ids),
                        member_query.exists(),
                        and_(
                            or_(*flocs_query),
                            or_(*workcenters_query),
                            or_(
                                self.schema.type == "SAP_Notification",
                                self.schema.type == "SAP_Work_Order",
                            ),
                        ),
                        and_(
                            or_(*flocs_query),
                            self.schema.type == "AHM",
                        ),
                    )
                )
            elif not flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id.in_(user_ids),
                        member_query.exists(),
                        # and_(
                        #     or_(*flocs_query),
                        #     or_(*workcenters_query),
                        #     or_(
                        #         self.schema.type == "SAP_Notification",
                        #         self.schema.type == "SAP_Work_Order",
                        #     ),
                        # ),
                        # and_(
                        #     or_(*flocs_query),
                        #     self.schema.type == "AHM",
                        # ),
                    )
                )
            elif flocs_query:
                query = query.filter(
                    or_(
                        self.schema.owner_id.in_(user_ids),
                        member_query.exists(),
                        # and_(
                        #     or_(*flocs_query),
                        #     or_(*workcenters_query),
                        #     or_(
                        #         self.schema.type == "SAP_Notification",
                        #         self.schema.type == "SAP_Work_Order",
                        #     ),
                        # ),
                        and_(
                            or_(*flocs_query),
                            self.schema.type == "AHM",
                        ),
                    )
                )

            del filters["my_team"]

        # ------------------------------------------------------------------------------------

        if "user" in filters:
            del filters["user"]

        if "global_text" in filters:
            """
            TEXT LIKE COLUMNS:
                -> title x
                -> description x
                -> type x
                -> priority x
                -> function_location x
                 -> member_ids x

                -> owner_id
                -> supervisor_id
                -> status
            """

            # FILTER ALL TEXT LIKE COLS
            filter_text = filters["global_text"].lower()

            member_query = (
                db.query(schemas.Action_Member_Association.id)
                .join(schemas.User, schemas.User.id == schemas.Action_Member_Association.user_id)
                .filter(schemas.Action_Member_Association.action_id == self.schema.id)
                .filter(
                    or_(
                        schemas.User.name.ilike(f"%{filter_text}%"),
                        schemas.User.email.ilike(f"%{filter_text}%"),
                    )
                )
            )

            query = query.filter(
                or_(
                    func.lower(self.schema.title).contains(filter_text),
                    func.lower(self.schema.description).contains(filter_text),
                    func.lower(self.schema.type).contains(filter_text),
                    func.lower(self.schema.functional_location).contains(filter_text),
                    member_query.exists(),
                )
            )

            del filters["global_text"]

        # -------------------------------------------------------------

        return super().__add_filters__(db, query, filters)

    # @property
    # def order_key(self):
    #     return None

    def get_items_by_rules(
        self,
        db: Session,
        filters: list[Rules],
        extra_filters,
        user,
        page,
        count,
        sort_by=["priority", "status", "date_due"],
        sort_desc=[False, False, False],
    ):
        def add_members_query(query, rules: list[Rule], mode: str):

            # helper functions
            def equals_query(uid):
                return (
                    db.query(schemas.Action_Member_Association.id)
                    .filter(schemas.Action_Member_Association.action_id == self.schema.id)
                    .filter(schemas.Action_Member_Association.user_id == uid)
                )

            def empty_query():
                return db.query(schemas.Action_Member_Association.id).filter(
                    schemas.Action_Member_Association.action_id == self.schema.id
                )

            # rules
            equals_uids = [x.value for x in rules if x.type == "equals"]
            not_equals_uids = [x.value for x in rules if x.type == "does_not_equal"]
            is_empty_uids = [x.value for x in rules if x.type == "is_empty"]
            is_not_empty_uids = [x.value for x in rules if x.type == "is_not_empty"]

            # build query
            final_query = []
            for x in equals_uids:
                if x:
                    final_query.append(equals_query(x).exists())

            for x in not_equals_uids:
                if x:
                    final_query.append(equals_query(x).exists() == False)

            if is_empty_uids:
                final_query.append(empty_query().exists() == False)

            if is_not_empty_uids:
                final_query.append(empty_query().exists())

            # apply query
            wrapper = or_ if mode == "or" else and_
            return query.filter(wrapper(*final_query))

        # ------------------------------------------

        query = db.query(schemas.Action)

        # ------------------------------------------

        # Permission layer

        # BASIC USER PERMISSIONS
        # ---------------------------
        # A basic user can see:
        #     [1]. Actions that they belong to (owner, member, supervisor)
        #             - these actions can have any privacy
        #     [2]. All PUBLIC actions
        #     [3]. All actions that are in a workgroup that I belong to
        #     [4]. Non-Archived actions only

        # get all actions that are associated with my workgroups

        workgroup_member_assoc_query = (
            select(schemas.Workgroup_Member_Association.workgroup_id)
            .where(schemas.Workgroup_Member_Association.user_id == user.id)
            .distinct()
        )
        workgroup_member_assoc_ids = db.scalars(workgroup_member_assoc_query).all()

        workgroup_admin_assoc_query = (
            select(schemas.Workgroup_Admin_Association.workgroup_id)
            .where(schemas.Workgroup_Admin_Association.user_id == user.id)
            .distinct()
        )
        workgroup_admin_assoc_ids = db.scalars(workgroup_admin_assoc_query).all()

        workgroup_owner_query = select(schemas.Workgroup.id).where(
            schemas.Workgroup.owner_id == user.id
        )
        workgroup_owner_ids = db.scalars(workgroup_owner_query).all()

        workgroup_ids = set(
            workgroup_member_assoc_ids + workgroup_admin_assoc_ids + workgroup_owner_ids
        )

        workgroup_action_query = (
            select(schemas.Workgroup_Action_Association.action_id)
            .where(schemas.Workgroup_Action_Association.workgroup_id.in_(workgroup_ids))
            .distinct()
        )
        action_ids = db.scalars(workgroup_action_query).all()

        # ------------------------------------------------

        # MY GROUPS FILTER - Show actions related to workgroups user is apart of
        if "my_groups" in extra_filters:
            # Actions associated to workgroups where the user is a member of, admin of, or owner of, that workgroup
            query = db.query(self.schema).filter(self.schema.id.in_(action_ids))
            del extra_filters["my_groups"]

        else:
            query = (
                db.query(self.schema)
                # .filter(self.schema.is_archived.isnot(True))
                .filter(
                    or_(
                        self.schema.owner_id == user.id,
                        self.schema.supervisor_id == user.id,
                        self.schema.id.in_(action_ids),
                        # workgroup_query.exists(),
                        self.schema.privacy == PrivacyEnum.PUBLIC,
                    )
                )
            )

        # ------------------------------------------

        overrides = dict(
            member_ids=add_members_query,
        )

        for filter in filters:
            if filter.field in overrides:
                query = overrides[filter.field](query, filter.rules, filter.mode)
                continue

            field = getattr(schemas.Action, filter.field, None)

            if field is None:
                continue

            rules = []

            for rule in filter.rules:
                rule_sql = RULE_SQL.get(rule.type, None)

                if rule_sql:
                    rules.append(rule_sql(field, rule.value))
                else:
                    print(f"Invalid rule type: {rule.type}")

            wrapper = or_ if filter.mode == "or" else and_

            query = query.filter(wrapper(*rules))

        # ------------------------------------------

        query = self.__add_filters__(db, query, extra_filters)

        # ------------------------------------------

        if not sort_by:
            sort_by = ["priority", "status", "date_due"]
            sort_desc = [False, False, False]

        query = self.__add_sorting__(query, sort_by, sort_desc)

        # ------------------------------------------

        return dict(items=query.limit(count).offset((page - 1) * count).all(), count=query.count())


class SAP_Notification_Action(CRUD_Base[schemas.SAP_Notification_Action]):
    pass


class SAP_Work_Order_Action(CRUD_Base[schemas.SAP_Work_Order_Action]):
    pass


class BMS_ACT_Action(CRUD_Base[schemas.BMS_ACT_Action]):
    pass


class BMS_CR_Action(CRUD_Base[schemas.BMS_CR_Action]):
    pass


class BMS_HZD_Action(CRUD_Base[schemas.BMS_HZD_Action]):
    pass


class BMS_ITR_Action(CRUD_Base[schemas.BMS_ITR_Action]):
    pass


class SMH_Action(CRUD_Base[schemas.SMH_Action]):
    pass


class AHM_Action(CRUD_Base[schemas.AHM_Action]):
    pass


class ACE_Action(CRUD_Base[schemas.ACE_Action]):
    pass


class Teams_Action(CRUD_Base[schemas.Teams_Action]):
    pass


class DEP_Action(CRUD_Base[schemas.DEP_Action]):
    pass


class Action_Comment(CRUD_Base[schemas.Action_Comment]):
    @property
    def order_key(self):
        return self.schema.created


class Action_Member_Association(CRUD_Base[schemas.Action_Member_Association]):
    pass


action = Action()
sap_notification_action = SAP_Notification_Action()
sap_work_order_action = SAP_Work_Order_Action()
bms_act_action = BMS_ACT_Action()
bms_cr_action = BMS_CR_Action()
bms_hzd_action = BMS_HZD_Action()
bms_itr_action = BMS_ITR_Action()
smh_action = SMH_Action()
ahm_action = AHM_Action()
ace_action = ACE_Action()
teams_action = Teams_Action()
dep_action = DEP_Action()
action_comment = Action_Comment()
action_member_association = Action_Member_Association()
