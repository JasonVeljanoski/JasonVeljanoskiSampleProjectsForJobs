from sqlalchemy import and_, func, not_, or_
from sqlalchemy.orm import aliased

from app import schemas

from .base import CRUD_Base, add_date_filter


class Investigation(CRUD_Base[schemas.Investigation]):
    sub_cruds = ["owners", "aplus_delay_events", "rems_delay_events"]

    def get_user_open_investigations(self, db, *, user_id):

        schema = aliased(self.schema)

        user_query = (
            db.query(schemas.Investigation_Owner_Association.id)
            .filter(schemas.Investigation_Owner_Association.investigation_id == schema.id)
            .filter(schemas.Investigation_Owner_Association.user_id == user_id)
        )
        return (
            db.query(schema)
            .filter(schema.is_archived.isnot(True))
            .filter(schema.status != schemas.StatusEnum.CLOSED)
            .filter(or_(schema.supervisor_id == user_id, user_query.exists()))
        ).all()

    def __add_filters__(self, db, query, filters):

        # DEFINE JOINS
        # -------------------------------------------------------------
        if "global_text" in filters or "site" in filters or "department" in filters:
            query = query.join(
                schemas.Equipment,
                and_(
                    schemas.Equipment.function_location == self.schema.function_location,
                    schemas.Equipment.equipment_description == self.schema.equipment_description,
                ),
                isouter=True,
            )

        if "show_mine" in filters or "owner_ids" in filters:
            query = query.join(
                schemas.Investigation_Owner_Association,
                self.schema.id == schemas.Investigation_Owner_Association.investigation_id,
                isouter=True,
            )

        if "causes" in filters:
            query = query.join(schemas.Root_Cause_Detail)

        # -------------------------------------------------------------

        if "show_relevant_flag" in filters:
            relevant_investigations = (
                db.query(schemas.Relevant_Investigation_Association)
                .filter(
                    schemas.Relevant_Investigation_Association.investigation_id
                    == filters["investigation_id"]
                )
                .all()
            )
            rel_inv_ids = [x.relevent_investigation_id for x in relevant_investigations]
            query = query.filter(self.schema.id.in_(rel_inv_ids))

            del filters["show_relevant_flag"]
        if "investigation_id" in filters:
            del filters["investigation_id"]

        # -------------------------------------------------------------

        if "global_text" in filters:
            """
            TEXT LIKE COLUMNS:
                -> site
                -> department
                -> function_location
                -> title
                -> description
                -> object_type
                -> damage_code
                -> cause_code

                ---

                -> equipment_description

                -> event_datetime
                -> completion_due_date
                -> date_closed
                -> updated
                -> created

                -> priority
                -> status
                -> investigation_type

                -> owner_ids
                -> supervisor_id
            """
            # FILTER ALL TEXT LIKE COLS
            filter_text = filters["global_text"].lower()
            query = query.filter(
                or_(
                    func.lower(schemas.Equipment.site).contains(filter_text),
                    func.lower(schemas.Equipment.department).contains(filter_text),
                    func.lower(self.schema.function_location).contains(filter_text),
                    func.lower(self.schema.title).contains(filter_text),
                    func.lower(self.schema.description).contains(filter_text),
                    func.lower(self.schema.object_type).contains(filter_text),
                    func.lower(self.schema.damage_code).contains(filter_text),
                    func.lower(self.schema.cause_code).contains(filter_text),
                )
            )

            del filters["global_text"]

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

        if "site" in filters:
            query = query.filter(schemas.Equipment.site.in_(filters["site"]))

            del filters["site"]

        if "department" in filters:
            query = query.filter(schemas.Equipment.department.in_(filters["department"]))

            del filters["department"]

        # -------------------------------------------------------------

        if "title" in filters:
            query = query.filter(func.lower(self.schema.title).contains(filters["title"].lower()))

            del filters["title"]

        # -------------------------------------------------------------

        if "blacklist_ids" in filters:
            query = query.filter(self.schema.id.not_in(filters["blacklist_ids"]))

        if "blacklist_ids" in filters:
            del filters["blacklist_ids"]

        # -------------------------------------------------------------

        if "show_mine" in filters:
            query = query.filter(
                or_(
                    schemas.Investigation.supervisor_id == filters["user_id"],
                    schemas.Investigation_Owner_Association.user_id == filters["user_id"],
                )
            )

            del filters["show_mine"]

        if "user_id" in filters:
            del filters["user_id"]

        # -------------------------------------------------------------

        if "owner_ids" in filters:
            query = query.filter(
                schemas.Investigation_Owner_Association.user_id.in_(filters["owner_ids"]),
            )
            del filters["owner_ids"]

        # -------------------------------------------------------------

        if "causes" in filters:
            query = query.filter(
                schemas.Root_Cause_Detail.cause_code.in_(filters["causes"]),
            )
            del filters["causes"]

        # -------------------------------------------------------------

        date_filters = dict(
            incident_date=self.schema.event_datetime,
            date_closed=self.schema.date_closed,
            completion_due_date=self.schema.completion_due_date,
            updated_date=self.schema.updated,
            created_date=self.schema.created,
        )

        for k, v in date_filters.items():
            query = add_date_filter(query, k, v, filters)

        # -------------------------------------------------------------

        if "effective_duration" in filters:

            min = filters["effective_duration"][0]
            max = filters["effective_duration"][1]

            if min == 0:

                query = query.filter(
                    or_(
                        self.schema.total_effective_duration == None,
                        self.schema.total_effective_duration >= min,
                    )
                )
            elif min > 0:
                query = query.filter(
                    self.schema.total_effective_duration >= min,
                )

            if max:
                query = query.filter(
                    or_(
                        self.schema.total_effective_duration == None,
                        self.schema.total_effective_duration <= max,
                    )
                )

            del filters["effective_duration"]

        if "event_duration" in filters:

            min = filters["event_duration"][0]
            max = filters["event_duration"][1]

            if min == 0:
                query = query.filter(
                    or_(
                        self.schema.total_event_duration == None,
                        self.schema.total_event_duration >= min,
                    )
                )
            elif min > 0:
                query = query.filter(
                    self.schema.total_event_duration >= min,
                )

            if max:
                query = query.filter(
                    or_(
                        self.schema.total_event_duration == None,
                        self.schema.total_event_duration <= max,
                    )
                )

            del filters["event_duration"]

        # -------------------------------------------------------------

        if "completed_steps" in filters:

            min = filters["completed_steps"][0]
            max = filters["completed_steps"][1]

            if min:
                query = query.filter(
                    or_(
                        self.schema.steps_completed == None,
                        self.schema.steps_completed >= min,
                    )
                )
            if max:
                query = query.filter(
                    or_(
                        self.schema.steps_completed == None,
                        self.schema.steps_completed <= max,
                    )
                )

            del filters["completed_steps"]

        # -------------------------------------------------------------

        return super().__add_filters__(db, query, filters)

    @property
    def order_key(self):
        return self.schema.event_datetime.desc()


class Investigation_Owner_Association(CRUD_Base[schemas.Investigation_Owner_Association]):
    pass


class Relevant_Investigation_Association(CRUD_Base[schemas.Relevant_Investigation_Association]):
    pass


class Flash_Report(CRUD_Base[schemas.Flash_Report]):
    pass


class Root_Cause_Detail(CRUD_Base[schemas.Root_Cause_Detail]):
    pass


class Shared_Learning(CRUD_Base[schemas.Shared_Learning]):
    pass


investigation = Investigation()
investigation_owner_association = Investigation_Owner_Association()
relevant_investigation_association = Relevant_Investigation_Association()
flash_report = Flash_Report()
root_cause_detail = Root_Cause_Detail()
shared_learning = Shared_Learning()
