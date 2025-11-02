from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, IntEnum
from .enums import FeedbackReason, FeedbackStatusEnum


class Feedback_Comment(Base):
    feedback_id = Column(Integer, ForeignKey("Feedback.id"))
    user_id = Column(Integer, ForeignKey("User.id"))
    comment = Column(String)
    feedback = relationship("Feedback", foreign_keys=[feedback_id], back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])


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

    comments = relationship("Feedback_Comment", back_populates="feedback", cascade="all,delete")
    general_attachments = relationship(
        "Feedback_Attachment", back_populates="feedback", cascade="all,delete"
    )
