from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, IntEnum
from .enums import FeedbackReason, FeedbackStatusEnum


class Feedback(Base):
    reason = Column(IntEnum(FeedbackReason))
    title = Column(String)
    page = Column(String)
    summary = Column(String)
    replicate = Column(String)
    created_by_id = Column(Integer, ForeignKey("User.id"))
    updated_by_id = Column(Integer, ForeignKey("User.id"))
    status = Column(IntEnum(FeedbackStatusEnum))
    closure_notes = Column(String)

    general_attachments = relationship(
        "Feedback_Attachment", back_populates="feedback", cascade="all,delete"
    )
    comments = relationship("Feedback_Comment", back_populates="feedback", cascade="all,delete")
