from datetime import date

from sqlalchemy import and_, func, not_, or_
from sqlalchemy.orm import aliased

from app import schemas
from app.schemas.enums import ActionSourceEnum

from .base import CRUD_Base, add_date_filter


class Action_Owner_Association(CRUD_Base[schemas.Action_Owner_Association]):
    pass


class Action_Member_Association(CRUD_Base[schemas.Action_Member_Association]):
    pass


class Action_Comment(CRUD_Base[schemas.Action_Comment]):
    pass


class Action(CRUD_Base[schemas.Action]):
    sub_cruds = ["owners", "members"]

    def get_user_open_actions(self, db, *, user_id):

        schema = aliased(self.schema)

        user_query = (
            db.query(schemas.Action_Owner_Association.id)
            .filter(schemas.Action_Owner_Association.action_id == schema.id)
            .filter(schemas.Action_Owner_Association.user_id == user_id)
        )

        return (
            (
                db.query(schema)
                .filter(schema.is_archived.isnot(True))
                .filter(schema.status != schemas.StatusEnum.CLOSED)
                .filter(
                    or_(
                        and_(
                            self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                            self.schema.five_why_id.isnot(None),
                        ),
                        and_(
                            self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                            self.schema.flash_report_id.isnot(None),
                        ),
                        and_(
                            self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                            self.schema.root_cause_detail_id.isnot(None),
                        ),
                        self.schema.is_historical == schemas.Historical.HISTORICAL,
                    )
                )
                .filter(or_(schema.supervisor_id == user_id, user_query.exists()))
            )
            .distinct(schema.id)
            .all()
        )

    def get_shared_learning_actions(self, db, investigation_id):
        """
        Shared Learnings actions
        - contain all actions of an investigation, excluding, flash report actions
        - filter out archived actions
        """
        return (
            db.query(self.schema)
            .filter(self.schema.investigation_id == investigation_id)
            .filter(self.schema.flash_report_id == None)
            .filter(self.schema.is_archived.is_not(True))
            .all()
        )

    def __add_filters__(self, db, query, filters):

        query = query.filter(
            or_(
                and_(
                    self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                    self.schema.five_why_id.isnot(None),
                ),
                and_(
                    self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                    self.schema.flash_report_id.isnot(None),
                ),
                and_(
                    self.schema.is_historical == schemas.Historical.NOT_HISTORICAL,
                    self.schema.root_cause_detail_id.isnot(None),
                ),
                self.schema.is_historical == schemas.Historical.HISTORICAL,
            )
        )

        # DEFINE JOINS
        # -------------------------------------------------------------
        if "show_mine" in filters or "owner_member_ids" in filters:
            query = query.join(schemas.Action_Owner_Association, isouter=True).join(
                schemas.Action_Member_Association,
                self.schema.id == schemas.Action_Member_Association.action_id,
                isouter=True,
            )

        if "function_location" in filters or "site" in filters or "department" in filters:
            query = query.join(schemas.Investigation).join(
                schemas.Equipment,
                and_(
                    schemas.Equipment.function_location == schemas.Investigation.function_location,
                    schemas.Equipment.equipment_description
                    == schemas.Investigation.equipment_description,
                ),
                isouter=True,
            )

        # -------------------------------------------------------------

        query = query.filter(self.schema.is_deleted.isnot(True))

        # -------------------------------------------------------------

        if "show_mine" in filters:
            query = query.filter(
                or_(
                    schemas.Action.supervisor_id == filters["user_id"],
                    schemas.Action_Owner_Association.user_id == filters["user_id"],
                    schemas.Action_Member_Association.user_id == filters["user_id"],
                )
            )

            del filters["show_mine"]

        if "user_id" in filters:
            del filters["user_id"]

        # -------------------------------------------------------------

        if "global_text" in filters:
            """
            TEXT LIKE COLUMNS:
                -> title
                -> description
            """

            # FILTER ALL TEXT LIKE COLS
            filter_text = filters["global_text"].lower()
            query = query.filter(
                or_(
                    func.lower(self.schema.title).contains(filter_text),
                    func.lower(self.schema.description).contains(filter_text),
                )
            )

            del filters["global_text"]

        # -------------------------------------------------------------

        if "source" in filters:
            flash_report_source = (
                and_(
                    self.schema.flash_report_id.isnot(None),
                    self.schema.five_why_id == None,
                    self.schema.root_cause_detail_id == None,
                )
                if ActionSourceEnum.FLASH_REPORT in filters["source"]
                else None
            )

            five_why_source = (
                and_(
                    self.schema.flash_report_id == None,
                    self.schema.five_why_id.isnot(None),
                    self.schema.root_cause_detail_id == None,
                )
                if ActionSourceEnum.FIVE_WHY in filters["source"]
                else None
            )

            root_cause_source = (
                and_(
                    self.schema.flash_report_id == None,
                    self.schema.five_why_id == None,
                    self.schema.root_cause_detail_id.isnot(None),
                )
                if ActionSourceEnum.ROOT_CAUSE in filters["source"]
                else None
            )

            # OR clause for multi-select feature
            query = query.filter(or_(flash_report_source, five_why_source, root_cause_source))

            del filters["source"]

        # -------------------------------------------------------------

        if "archive_status" in filters:

            if schemas.ArchiveStatus.Active == filters["archive_status"]:
                query = query.filter(
                    or_(
                        self.schema.is_archived == False,
                        self.schema.is_archived == None,
                    )
                )

            elif schemas.ArchiveStatus.Archived == filters["archive_status"]:
                query = query.filter(self.schema.is_archived == True)

            del filters["archive_status"]

        # -------------------------------------------------------------

        if "function_location" in filters:
            query = query.filter(
                schemas.Investigation.function_location.in_(filters["function_location"]),
            )

            del filters["function_location"]

        # -------------------------------------------------------------

        if "site" in filters or "department" in filters:

            if "site" in filters:
                """for reference
                SELECT
                    count(*)
                FROM "Action" JOIN "Investigation" ON "Investigation".id = "Action".investigation_id LEFT OUTER JOIN "Equipment" ON "Equipment".function_location = "Investigation".function_location AND "Equipment".equipment_description = "Investigation".equipment_description
                WHERE (
                        "Action".is_historical = 0  and "Action".five_why_id IS NOT NULL
                        OR
                        "Action".is_historical = 0 AND "Action".flash_report_id IS NOT NULL
                        OR "Action".is_historical = 1
                    )
                    AND (
                        "Action".is_archived = false OR "Action".is_archived IS NULL)
                        AND
                        "Equipment".site IN ('Solomon')
                """
                query = query.filter(schemas.Equipment.site.in_(filters["site"]))

                del filters["site"]

            if "department" in filters:
                """for reference
                SELECT
                    count(*)
                FROM "Action" JOIN "Investigation" ON "Investigation".id = "Action".investigation_id LEFT OUTER JOIN "Equipment" ON "Equipment".function_location = "Investigation".function_location AND "Equipment".equipment_description = "Investigation".equipment_description
                WHERE (
                        "Action".is_historical = 0  and "Action".five_why_id IS NOT NULL
                        OR
                        "Action".is_historical = 0 AND "Action".flash_report_id IS NOT NULL
                        OR "Action".is_historical = 1
                    )
                    AND (
                        "Action".is_archived = false OR "Action".is_archived IS NULL)
                        AND
                        "Equipment".department IN ('Process Plant')
                """
                query = query.filter(schemas.Equipment.department.in_(filters["department"]))

                del filters["department"]

        # -------------------------------------------------------------

        if "owner_member_ids" in filters:
            query = query.filter(
                or_(
                    schemas.Action_Owner_Association.user_id.in_(filters["owner_member_ids"]),
                    schemas.Action_Member_Association.user_id.in_(filters["owner_member_ids"]),
                )
            )
            del filters["owner_member_ids"]

        # -------------------------------------------------------------

        if "title" in filters:
            query = query.filter(func.lower(self.schema.title).contains(filters["title"].lower()))

            del filters["title"]

        # -------------------------------------------------------------

        date_filters = dict(
            date_due=self.schema.date_due,
            date_closed=self.schema.date_closed,
            updated_date=self.schema.updated,
            created_date=self.schema.created,
        )

        for k, v in date_filters.items():
            query = add_date_filter(query, k, v, filters)

        # -------------------------------------------------------------

        return super().__add_filters__(db, query, filters)

    @property
    def order_key(self):
        return self.schema.updated.desc()

    def get_all_active(self, db):
        query = db.query(schemas.Action).filter(schemas.Action.is_archived.isnot(True))
        return query.all()


action_owner_association = Action_Owner_Association()
action_member_association = Action_Member_Association()
action = Action()
action_comment = Action_Comment()
