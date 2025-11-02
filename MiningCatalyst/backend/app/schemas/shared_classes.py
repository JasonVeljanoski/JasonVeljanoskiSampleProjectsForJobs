from sqlalchemy import Boolean, Column, Integer, String

from .base import TZDateTime


class __Deletable__:
    delete_user_id = Column(Integer)
    delete_datetime = Column(TZDateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class __ENUM__:
    label = Column(String, nullable=False)
    order = Column(Integer)
    color = Column(String)
