import datetime as dt
import enum

from turtle import back
from datetime import datetime
from .base import Base, BaseID


class General_Attachment(BaseID):
    title: str = None
    description: str = None
    unique_filename: str = None
    filename: str = None
    size: int = None
    extension: str = None
    uploaded_by: int = None
    deleted: bool = None
    deleted_date: datetime = None
    deleted_by: int = None
