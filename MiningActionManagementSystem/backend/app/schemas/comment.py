from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship

from .base import Base


class Comment(Base):
    user_id = Column(Integer, ForeignKey("User.id"))
    comment = Column(String)

    @declared_attr
    def type(cls):
        return Column(String)

    @declared_attr
    def __mapper_args__(self):
        if has_inherited_table(self):
            return {"polymorphic_identity": self.__name__[:-8]}
        return {"polymorphic_on": self.type}

    user = relationship("User", foreign_keys=[user_id])


# ---------------------------------


class Action_Comment(Comment):
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))

    @property
    def item_id(self):
        return self.feedback_id

    @item_id.setter
    def item_id(self, value):
        self.feedback_id = value

    action = relationship("Action", foreign_keys=[action_id], back_populates="comments")


# ---------------------------------


class Workgroup_Comment(Comment):
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id", ondelete="CASCADE"))

    @property
    def item_id(self):
        return self.workgroup_id

    @item_id.setter
    def item_id(self, value):
        self.workgroup_id = value

    workgroup = relationship("Workgroup", foreign_keys=[workgroup_id], back_populates="comments")


# ---------------------------------


class Feedback_Comment(Comment):
    feedback_id = Column(Integer, ForeignKey("Feedback.id", ondelete="CASCADE"))

    @property
    def item_id(self):
        return self.feedback_id

    @item_id.setter
    def item_id(self, value):
        self.feedback_id = value

    feedback = relationship("Feedback", foreign_keys=[feedback_id], back_populates="comments")
