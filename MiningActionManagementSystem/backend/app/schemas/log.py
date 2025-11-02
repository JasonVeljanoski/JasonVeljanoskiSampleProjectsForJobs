from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean

from .base import Base, TZDateTime


class Log(Base):
    type = Column(String)
    user_id = Column(Integer, ForeignKey("User.id"))
    sync_uuid = Column(String)
    total_actions_created = Column(Integer)
    total_actions_archived = Column(Integer)
    total_actions_updated = Column(Integer)
    action_id = Column(Integer, ForeignKey("Action.id"))
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id"))

    # Relates to Teams Sync
    total_workgroups_created = Column(Integer)
    workgroup_ids_involved = Column(String)
    user_ids_involved = Column(String)


"""
class Log(Base):
    user_id = Column(Integer, ForeignKey("User.id"))

    @declared_attr
    def type(cls):
        return Column(String)

    @declared_attr
    def __mapper_args__(self):
        if has_inherited_table(self):
            return {"polymorphic_identity": self.__name__[:-4]}
        return {"polymorphic_on": self.type}


class Action_Log(Log):
    action_id = Column(Integer, ForeignKey("Action.id"))

    @property
    def item_id(self):
        return self.action_id

    @item_id.setter
    def item_id(self, value):
        self.action_id = value


class Workgroup_Log(Log):
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id"))

    @property
    def item_id(self):
        return self.workgroup_id

    @item_id.setter
    def item_id(self, value):
        self.workgroup_id = value

"""

# -------------------------------------------------------------------------


class Update_History(Base):
    user_id = Column(Integer, ForeignKey("User.id"))
    active = Column(Boolean, default=False)
    content = Column(String)


# -------------------------------------------------------------------------
