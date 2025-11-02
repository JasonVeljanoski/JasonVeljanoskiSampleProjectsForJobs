from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from .base import Base, IntEnum
from .enums import NotificationTypeEnum


class Notification(Base):
    title = Column(String)
    message = Column(String)
    tags = Column(ARRAY(String))
    type = Column(IntEnum(NotificationTypeEnum))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))

    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
