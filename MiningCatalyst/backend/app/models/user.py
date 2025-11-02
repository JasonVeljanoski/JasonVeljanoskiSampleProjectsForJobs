import datetime as dt

from .base import BaseID


class UserBasic(BaseID):
    name: str = None
    email: str = None
    supervisor_id: int = None


class User(BaseID):
    name: str = None
    email: str = None
    is_user: bool = None
    last_logged_in: dt.datetime = None
    access: int = None
    supervisor_id: int = None
