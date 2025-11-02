from app import crud, models, schemas, utils
from app.schemas.enums import PrivacyEnum
from app.schemas.user import Access
from app.utils import errors, get_time_now
from fastapi import APIRouter, Body, Depends
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .base import RULE_SQL, CRUD_Base, Rule, Rules, add_date_filter


class Workgroup(CRUD_Base[schemas.Workgroup]):
    sub_cruds = ["actions", "action_associations", "member_associations", "admin_associations"]

    def get_basic_user_workgroups_page(
        self, db, user_id, page, count, sort_by=["id"], sort_desc=[True], **filters
    ):
        """
        BASIC USER PERMISSIONS
        ---------------------------
        A basic user can see:
            [1]. Workgroups that they belong to (owner, supervisor, the like)
                    - these workgroups can have any privacy (confidential, public, declined, requested, the like)
            [2]. All PUBLIC workgroups
        """
        member_query = (
            db.query(schemas.Workgroup_Member_Association.id)
            .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Member_Association.user_id == user_id)
        )
        admin_query = (
            db.query(schemas.Workgroup_Admin_Association.id)
            .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
            .filter(schemas.Workgroup_Admin_Association.user_id == user_id)
        )

        query = (
            db.query(self.schema)
            # .filter(self.schema.is_archived.isnot(True))
            .filter(
                or_(
                    self.schema.owner_id == user_id,
                    member_query.exists(),
                    admin_query.exists(),
                    self.schema.privacy == PrivacyEnum.PUBLIC,
                )
            )
        )

        # ------------------------------------------
        # todo - this code is copied from crud base. make wrapper function in crud base as it is used in multiple places. i tried, i failed. (it's late)

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

    # ------------------------------------------------------------------------------------------------

    def get_system_admin_workgroups_page(
        self, db, user_id, page, count, sort_by=["id"], sort_desc=[True], **filters
    ):
        """
        SYSTEM ADMIN PERMISSIONS
        ---------------------------
        A system admin can see:
            [1]. All workgroups with no restrictions (could change)
        """
        # ADMIN ONLY METHOD
        user = crud.user.get(db, user_id)
        if user.access < Access.ADMIN:
            raise errors.PermissionDeniedException()

        return crud.workgroup.get_page(db, page, count, sort_by, sort_desc, **filters)

    # ------------------------------------------------------------------------------------------------

    # Returns workgroups that a user can EDIT -- used to add actions to workgroups from the edit action form
    def get_workgroup_titles(self, db, user):
        """
        Any user can EDIT a workgroup where:
            1) User is admin of the workgroup
            
            2) User is assigned to the workgroup (Owner)
        """

        # Get workgroup IDs for where admin of that workgroup is the user
        workgroups_admin_query = (
            db.query(schemas.Workgroup_Admin_Association.workgroup_id)
            .where(schemas.Workgroup_Admin_Association.user_id == user.id)
            .distinct()
        )
        workgroups_admin_ids = db.scalars(workgroups_admin_query)

        # Complete criteria satisfying 1) & 2)
        workgroups_editable_query = db.query(schemas.Workgroup).filter(or_(schemas.Workgroup.id.in_(workgroups_admin_ids), schemas.Workgroup.owner_id == user.id))
        return workgroups_editable_query.all()

    # -----------------------------------------------------------------------------------------------

    def update_privacy(self, db, user, privacy, workgroup_id):
        """
        Update privacy of a workgroup with effects on Actions.

            Please reference "Everything Privacy in Action Centre for Excellence" pptx document for more information.
            Or ask Jason for a copy of the document.
        """

        def edit_actions_privacy(actions, privacy):
            for action in actions:
                crud.action.update_privacy(db, action.id, privacy)

        # SETUP
        edits = crud.workgroup.get(db, id=workgroup_id)
        workgroup_actions = edits.actions

        # ------------------------------------------------------------------------------
        # * REQUESTED = CONFIDENTIAL
        # -----------------------------------------------------------------------------
        if privacy == PrivacyEnum.CONFIDENTIAL:

            # public ---> confidential  OR confidential -> confidential
            # [1]. Remove all action associations with other workgroups
            # [2]. Make the actions confidential.
            # Notes:
            #   The confidential actions will only exist in this workgroup.
            #   Users should receive sufficient warning messages in the presentation layer before agreeing to changes.

            # [1]. Remove ALL action associations with other workgroups
            for action in workgroup_actions:
                crud.workgroup_action_association.delete_by_action_id(db, action.id)

            # Add association for this workgroup back in
            for action in workgroup_actions:
                crud.workgroup_action_association.create(
                    db,
                    schemas.Workgroup_Action_Association(
                        workgroup_id=workgroup_id, action_id=action.id
                    ),
                )

                # [2]. Make the actions confidential.
            edit_actions_privacy(workgroup_actions, PrivacyEnum.CONFIDENTIAL)

        # ------------------------------------------------------------------------------
        # * REQUESTED = PUBLIC FROM CONFIDENTIAL
        # ------------------------------------------------------------------------------
        elif privacy == PrivacyEnum.PUBLIC:
            # confidential ---> public
            # [1]. Actions get a public privacy
            # Notes:
            #   The public actions will only exist in this workgroup (by consequence of being in a Confidential workgroup).
            edit_actions_privacy(workgroup_actions, privacy)

        # ------------------------------------------------------------------------------

        # UPDATE WORKGROUP PRIVACY
        db.query(schemas.Workgroup).filter(schemas.Workgroup.id == workgroup_id).update(
            {
                "privacy": privacy,
                "updated": get_time_now(),
            }
        )
        db.commit()

    # -------------------------------------------------------------

    def __add_filters__(self, db, query, filters):

        # DEFINE JOINS HERE
        if "global_text" in filters:
            query = query.join(schemas.User, schemas.User.id == self.schema.owner_id)

        # -------------------------------------------------------------

        if "global_text" in filters:
            """
            TEXT LIKE COLUMNS:
                -> title x
                -> description x
                -> owner x
                -> member x
                -> admin x
            """

            filter_text = filters["global_text"].lower()

            member_query = (
                db.query(schemas.Workgroup_Member_Association.id)
                .join(schemas.User, schemas.User.id == schemas.Workgroup_Member_Association.user_id)
                .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
                .filter(
                    or_(
                        schemas.User.name.ilike(f"%{filter_text}%"),
                        schemas.User.email.ilike(f"%{filter_text}%"),
                    )
                )
            )

            admin_query = (
                db.query(schemas.Workgroup_Admin_Association.id)
                .join(schemas.User, schemas.User.id == schemas.Workgroup_Admin_Association.user_id)
                .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
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
                    func.lower(self.schema.functional_location).contains(filter_text),
                    member_query.exists(),
                    admin_query.exists(),
                    schemas.User.name.ilike(f"%{filter_text}%"),
                    schemas.User.email.ilike(f"%{filter_text}%"),
                )
            )

            del filters["global_text"]

        # -------------------------------------------------------------

        return super().__add_filters__(db, query, filters)

    # -------------------------------------------------------------

    def get_items_by_rules(
        self,
        db: Session,
        filters: list[Rules],
        extra_filters,
        user,
        page,
        count,
        sort_by=["updated", "is_active"],
        sort_desc=[True, False],
    ):
        def add_members_query(query, rules: list[Rule], mode: str):

            # helper functions
            def equals_query(uid):
                return (
                    db.query(schemas.Workgroup_Member_Association.id)
                    .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
                    .filter(schemas.Workgroup_Member_Association.user_id == uid)
                )

            def empty_query():
                return db.query(schemas.Workgroup_Member_Association.id).filter(
                    schemas.Workgroup_Member_Association.workgroup_id == self.schema.id
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

        def add_admin_query(query, rules: list[Rule], mode: str):

            # helper functions
            def equals_query(uid):
                return (
                    db.query(schemas.Workgroup_Admin_Association.id)
                    .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
                    .filter(schemas.Workgroup_Admin_Association.user_id == uid)
                )

            def empty_query():
                return db.query(schemas.Workgroup_Admin_Association.id).filter(
                    schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id
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

        query = db.query(schemas.Workgroup)

        overrides = dict(
            member_ids=add_members_query,
            admin_ids=add_admin_query,
        )

        for filter in filters:
            if filter.field in overrides:
                query = overrides[filter.field](query, filter.rules, filter.mode)
                continue

            field = getattr(schemas.Workgroup, filter.field, None)

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

        # ------------------------------------------

        # Permissions layer - show workgroups depending on access rules
        # Basic user:
        #   All public workgroups
        #   All workgroups that user is a member of, admin of, or owner of, regardless of privacy
        # Admin + Super Admin users:
        #   See ALL workgroups, regardless of privacy

        if "my_groups" in extra_filters:
            query = query.filter(
                or_(
                    self.schema.owner_id == user.id,
                    db.query(schemas.Workgroup_Member_Association.id)
                    .filter(schemas.Workgroup_Member_Association.workgroup_id == self.schema.id)
                    .filter(schemas.Workgroup_Member_Association.user_id == user.id)
                    .exists(),
                    db.query(schemas.Workgroup_Admin_Association.id)
                    .filter(schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id)
                    .filter(schemas.Workgroup_Admin_Association.user_id == user.id)
                    .exists(),
                )
            )
            del extra_filters["my_groups"]

        else:
            query = query.filter(
                or_(
                    self.schema.privacy == schemas.enums.PrivacyEnum.PUBLIC,
                    and_(
                        self.schema.privacy != schemas.enums.PrivacyEnum.PUBLIC,
                        or_(
                            self.schema.owner_id == user.id,
                            db.query(schemas.Workgroup_Member_Association.id)
                            .filter(
                                schemas.Workgroup_Member_Association.workgroup_id == self.schema.id
                            )
                            .filter(schemas.Workgroup_Member_Association.user_id == user.id)
                            .exists(),
                            db.query(schemas.Workgroup_Admin_Association.id)
                            .filter(
                                schemas.Workgroup_Admin_Association.workgroup_id == self.schema.id
                            )
                            .filter(schemas.Workgroup_Admin_Association.user_id == user.id)
                            .exists(),
                        ),
                    ),
                )
            )

        # ------------------------------------------

        query = self.__add_filters__(db, query, extra_filters)

        if not sort_by:
            sort_by = ["updated", "is_active"]
            sort_desc = [True, False]

        query = self.__add_sorting__(query, sort_by, sort_desc)

        # ------------------------------------------

        """
        items = query.limit(count).all()
        for itema in items:
            print(itema.actions)
        """

        return dict(items=query.limit(count).offset((page - 1) * count).all(), count=query.count())

    # -------------------------------------------------------------

    @property
    def order_key(self):
        return self.schema.updated


class Workgroup_Action_Association(CRUD_Base[schemas.Workgroup_Action_Association]):
    def delete_by_workgroup_id(self, db, workgroup_id):
        db.query(self.schema).filter(self.schema.workgroup_id == workgroup_id).delete()
        db.commit()

    def delete_by_action_id(self, db, action_id):
        db.query(self.schema).filter(self.schema.action_id == action_id).delete()
        db.commit()

    def append_action_to_workgroup(
        self,
        db,
        workgroup_id,
        action_id,
        workgroup_privacy,
        action_privacy,
    ):
        """
        [0]. Any public action can be appended to any public workgroup.
        [1]. For all other cases (confidental actions or adding public actions to confidential workgroups)
            -> remove all associations of action to other workgroups
            -> change action to appropriate status
        """

        # SANITY
        check_dups = crud.workgroup_action_association.get_kw(
            db, workgroup_id=workgroup_id, action_id=action_id
        )
        if check_dups:
            return utils.errors.CustomException

        # [0]. Adding public actions to a public workgroup occurs as normal
        if workgroup_privacy == PrivacyEnum.PUBLIC and action_privacy == PrivacyEnum.PUBLIC:
            obj = schemas.Workgroup_Action_Association(
                workgroup_id=workgroup_id, action_id=action_id
            )
            db.add(obj)
            db.commit()
            return
        # [1]. For all other cases (confidental actions or adding public actions to confidential workgroups)
        else:
            crud.workgroup_action_association.delete_by_action_id(db, action_id)

            action_privacy = None
            if workgroup_privacy == PrivacyEnum.PUBLIC:
                action_privacy = PrivacyEnum.PUBLIC
            elif workgroup_privacy == PrivacyEnum.CONFIDENTIAL:
                action_privacy = PrivacyEnum.CONFIDENTIAL
            else:
                raise utils.errors.CustomException

            crud.action.update_privacy(db, action_id, action_privacy)

            crud.workgroup_action_association.create(
                db,
                models.Workgroup_Action_Association(workgroup_id=workgroup_id, action_id=action_id),
            )


class Workgroup_Member_Association(CRUD_Base[schemas.Workgroup_Member_Association]):
    pass


class Workgroup_Admin_Association(CRUD_Base[schemas.Workgroup_Admin_Association]):
    pass


class Workgroup_Comment(CRUD_Base[schemas.Workgroup_Comment]):
    @property
    def order_key(self):
        return self.schema.created


workgroup = Workgroup()
workgroup_action_association = Workgroup_Action_Association()
workgroup_member_association = Workgroup_Member_Association()
workgroup_admin_association = Workgroup_Admin_Association()
workgroup_comment = Workgroup_Comment()
