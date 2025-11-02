import enum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.sql.sqltypes import Boolean

from .base import Base, IntEnum, LowercaseString, TZDateTime


class Access(enum.IntEnum):
    READER = 0
    WRITER = 1
    ADMIN = 2
    SUPER = 3


class User(Base):
    name = Column(String)
    email = Column(LowercaseString, unique=True, index=True)
    supervisor_id = Column(Integer, ForeignKey("user.id"))
    job_title = Column(String)
    sap_number = Column(Integer)

    # -----------------------------------------------

    is_user = Column(Boolean, default=False)  # todo: can remove this when logs are in place
    last_logged_in = Column(TZDateTime)  # todo: can remove this when logs are in place
    access = Column(IntEnum(Access), nullable=False, default=Access.WRITER)

    # -----------------------------------------------

    @property
    def is_writer(self):
        return self.access >= Access.WRITER

    @property
    def is_admin(self):
        return self.access >= Access.ADMIN

    @property
    def is_super(self):
        return self.access >= Access.SUPER
