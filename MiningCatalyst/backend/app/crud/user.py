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
    
    @property
    def order_key(self):
        return self.schema.name


user = User()
