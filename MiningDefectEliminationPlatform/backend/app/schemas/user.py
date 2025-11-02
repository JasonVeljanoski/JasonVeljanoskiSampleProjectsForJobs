import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base, IntEnum, LowercaseString, TZDateTime


class Access(enum.IntEnum):
    READER = 1
    WRITER = 2
    ADMIN = 3


def default_watched_groups():
    return dict(sites=None, departments=None, object_types=None, show_all=False)


class User(Base):
    name = Column(String)
    email = Column(LowercaseString, unique=True, index=True)

    job_title = Column(String)
    sap_number = Column(Integer, unique=True, index=True)

    location_id = Column(Integer, ForeignKey("Team.id"))
    team_name = Column(String)
    supervisor_id = Column(Integer, ForeignKey("User.id"))

    is_user = Column(Boolean, default=False)
    last_logged_in = Column(TZDateTime)

    access = Column(IntEnum(Access), default=Access.WRITER)

    watched_groups = Column(JSONB, default=default_watched_groups)

    @property
    def is_writer(self):
        return self.access >= Access.WRITER

    @property
    def is_admin(self):
        return self.access >= Access.ADMIN

    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
