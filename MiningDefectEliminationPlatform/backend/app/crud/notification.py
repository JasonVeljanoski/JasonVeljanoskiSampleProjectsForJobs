from app import schemas
from .base import CRUD_Base


class Notification(CRUD_Base[schemas.Notification]):
    def get_notifications_by_user(self, db, *, user_id):
        query = (
            db.query(schemas.Notification)
            .filter(schemas.Notification.user_id == user_id)
            .filter(schemas.Notification.is_deleted != True)
            .order_by(schemas.Notification.created.desc())
        )
        return query.all()

    @property
    def order_key(self):
        return self.schema.created


notification = Notification()
