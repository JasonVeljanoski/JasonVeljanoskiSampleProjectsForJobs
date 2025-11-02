from app import schemas
from sqlalchemy import and_, func, or_

from .base import CRUD_Base, add_date_filter


class Feedback_Comment(CRUD_Base[schemas.Feedback_Comment]):
    pass


class Feedback(CRUD_Base[schemas.Feedback]):
    def __add_filters__(self, db, query, filters):

        if "id" in filters:
            query = query.filter(self.schema.id == int(filters["id"]))

            del filters["id"]

        # -------------------------------------------------------------

        if "user_id" in filters:
            query = query.filter(self.schema.created_by_id == filters["user_id"])

            del filters["user_id"]

        # -------------------------------------------------------------

        if "reason" in filters:

            query = query.filter(self.schema.reason.in_(filters["reason"]))

            del filters["reason"]

        # -------------------------------------------------------------

        if "global_text" in filters:
            """
            TEXT LIKE COLUMNS:
                -> title
                -> page
                -> summary
                -> replicate
            """

            # FILTER ALL TEXT LIKE COLS
            filter_text = filters["global_text"].lower()
            query = query.filter(
                or_(
                    func.lower(self.schema.title).contains(filter_text),
                    func.lower(self.schema.page).contains(filter_text),
                    func.lower(self.schema.summary).contains(filter_text),
                    func.lower(self.schema.replicate).contains(filter_text),
                )
            )

            del filters["global_text"]

        # -------------------------------------------------------------

        date_filters = dict(
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


feedback_comment = Feedback_Comment()
feedback = Feedback()
