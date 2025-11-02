from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean

from .base import Base, TZDateTime


class General_Attachment(Base):
    title = Column(String)
    description = Column(String)
    unique_filename = Column(String)
    filename = Column(String)
    size = Column(Integer)
    uploaded_by = Column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
    )
    deleted = Column(Boolean)
    deleted_date = Column(TZDateTime)
    deleted_by = Column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
    )

    @declared_attr
    def type(cls):
        return Column(String)

    @declared_attr
    def __mapper_args__(self):
        if has_inherited_table(self):
            return {"polymorphic_identity": self.__name__[:-11]}
        return {"polymorphic_on": self.type}

    @property
    def extension(self):
        return self.filename.split(".")[-1]


class Feedback_Attachment(General_Attachment):
    feedback_id = Column(
        Integer,
        ForeignKey("Feedback.id", ondelete="CASCADE"),
    )

    @property
    def item_id(self):
        return self.feedback_id

    @item_id.setter
    def item_id(self, value):
        self.feedback_id = value

    feedback = relationship(
        "Feedback", back_populates="general_attachments", foreign_keys=[feedback_id]
    )


class Action_Attachment(General_Attachment):
    action_id = Column(
        Integer,
        ForeignKey("Action.id", ondelete="CASCADE"),
    )

    @property
    def item_id(self):
        return self.action_id

    @item_id.setter
    def item_id(self, value):
        self.action_id = value

    action = relationship(
        "ACE_Action", back_populates="general_attachments", foreign_keys=[action_id]
    )


class Workgroup_Attachment(General_Attachment):
    workgroup_id = Column(
        Integer,
        ForeignKey("Workgroup.id", ondelete="CASCADE"),
    )

    @property
    def item_id(self):
        return self.workgroup_id

    @item_id.setter
    def item_id(self, value):
        self.workgroup_id = value

    workgroup = relationship(
        "Workgroup", back_populates="general_attachments", foreign_keys=[workgroup_id]
    )
