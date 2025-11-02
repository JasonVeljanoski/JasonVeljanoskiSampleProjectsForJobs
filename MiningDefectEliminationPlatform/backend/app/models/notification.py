from .base import BaseID
from app.schemas.enums import NotificationTypeEnum


class Notification(BaseID):
    title: str = None
    message: str = None
    tags: list[str] = []
    type: NotificationTypeEnum = None
    is_read: bool = None
    is_deleted: bool = None
    user_id: int = None
