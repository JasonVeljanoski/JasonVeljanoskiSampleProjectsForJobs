from app import schemas
from .base import CRUD_Base

from sqlalchemy import func


class User(CRUD_Base[schemas.User]):
    def __add_filters__(self, db, query, filters):

        if "user" in filters:
            query = query.filter(func.lower(self.schema.name).contains(filters["user"].lower()))

            del filters["user"]

        return super().__add_filters__(db, query, filters)

    # -------------------------------------------------------------


user = User()
