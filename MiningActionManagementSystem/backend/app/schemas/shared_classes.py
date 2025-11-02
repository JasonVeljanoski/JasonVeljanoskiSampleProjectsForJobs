from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table, Boolean

from .base import TZDateTime


class __Archive_Details__:
    archive_user_id = Column(Integer)
    archive_datetime = Column(TZDateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
