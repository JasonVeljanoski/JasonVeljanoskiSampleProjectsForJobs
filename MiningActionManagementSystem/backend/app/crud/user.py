from sqlalchemy import func
from sqlalchemy.sql.expression import and_, or_

from app import crud, schemas, utils

from .base import CRUD_Base


class User(CRUD_Base[schemas.User]):
    def get_local_admin(self, db):
        admin = self.get_kw_single(db, email="enco_admin@fmgl.com.au")

        if admin:
            return admin

        return self.create(
            db,
            schemas.User(
                name="Local Admin",
                email="enco_admin@fmgl.com.au",
                access=schemas.Access.SUPER,
                is_user=True,
            ),
        )

    def __add_filters__(self, db, query, filters):

        if "global_text" in filters:
            global_text = filters.get("global_text").lower()

            query = query.filter(
                or_(
                    func.lower(self.schema.name).like(f"%{global_text}%"),
                    func.lower(self.schema.email).like(f"%{global_text}%"),
                    func.lower(self.schema.job_title).like(f"%{global_text}%"),
                )
            )

            del filters["global_text"]

        return super().__add_filters__(db, query, filters)

    @property
    def order_key(self):
        return self.schema.name


user = User()
