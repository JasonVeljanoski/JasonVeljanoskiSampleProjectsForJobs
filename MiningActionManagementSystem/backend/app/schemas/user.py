import enum

from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean

from .base import Base, IntEnum, LowercaseString, TZDateTime


class Access(enum.IntEnum):
    READER = 0
    WRITER = 1
    ADMIN = 2
    SUPER = 3


class User(Base):
    sap_number = Column(Integer, unique=True, index=True)
    email = Column(LowercaseString, unique=True, index=True)
    name = Column(String)
    job_title = Column(String)

    microsoft_id = Column(String)

    # ---

    functional_locations = Column(ARRAY(String))
    work_centers = Column(ARRAY(String))
    txoilsample = Column(Boolean)

    # ---

    back_to_back_id = Column(Integer, ForeignKey("User.id"))
    back_to_back = relationship("User", foreign_keys=[back_to_back_id])

    # ---

    supervisor_id = Column(Integer, ForeignKey("User.id"))

    # ---

    is_user = Column(Boolean, default=False)
    last_logged_in = Column(TZDateTime)

    # ---

    dont_show_news_again = Column(Boolean, default=False)

    # ---

    access = Column(IntEnum(Access), nullable=False, default=Access.WRITER)

    @property
    def is_writer(self):
        return self.access >= Access.WRITER

    @property
    def is_admin(self):
        return self.access >= Access.ADMIN

    @property
    def is_super(self):
        return self.access >= Access.SUPER
