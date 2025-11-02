from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table

from .base import TZDateTime


class __Archive_Details__:
    archive_user_id = Column(Integer)
    archive_datetime = Column(TZDateTime, nullable=True)
    is_archived = Column(Boolean, default=False)


class __Deletable__:
    delete_user_id = Column(Integer)
    delete_datetime = Column(TZDateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
