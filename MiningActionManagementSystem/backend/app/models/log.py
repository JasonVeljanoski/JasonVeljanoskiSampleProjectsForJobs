import datetime as dt
import enum
from datetime import datetime
from turtle import back

from .base import Base, BaseID


class Log(BaseID):
    type: str = None
    user_id: int = None
    action_id: int = None
    workgroup_id: int = None


class Update_History(BaseID):
    user_id: int = None
    active: bool = False
    content: str = None
