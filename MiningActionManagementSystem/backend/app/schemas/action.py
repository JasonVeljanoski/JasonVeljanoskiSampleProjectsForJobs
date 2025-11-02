from app.schemas.enums import ActionTagEnum, LinkedSystemEnum, PriorityEnum, PrivacyEnum, StatusEnum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified

from .base import Base, IntEnum, StrEnum, TZDateTime
from .shared_classes import __Archive_Details__
from .user import User
from .workgroup import Workgroup_Action_Association


# -----------------------------------------
# Association Tables
# -----------------------------------------
class Action_Member_Association(Base):
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


# ------------------------------------------------------------------------------------------


class MetadataField:
    def __init__(self, default=None):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, cls):
        return obj.metadata.get(self._name, self._default)

    def __set__(self, obj, value):
        flag_modified(obj, "metadata")
        obj.metadata[self._name] = value


class Action(Base, __Archive_Details__):
    # COMMON FIELDS
    title = Column(String)
    description = Column(String)

    priority = Column(IntEnum(PriorityEnum), default=PriorityEnum.UNKNOWN)
    owner_id = Column(Integer, ForeignKey("User.id"))
    supervisor_id = Column(Integer, ForeignKey("User.id"))

    source_created = Column(TZDateTime)
    source_updated = Column(TZDateTime)
    start_date = Column(TZDateTime)
    date_due = Column(TZDateTime)

    privacy = Column(IntEnum(PrivacyEnum), nullable=False, default=PrivacyEnum.PUBLIC)
    status = Column(IntEnum(StatusEnum))

    date_closed = Column(TZDateTime)

    # ACTION TYPE
    source_id = Column(String)

    # OTHER
    completed = Column(Integer, default=0)
    functional_location = Column(String)
    work_center = Column(String)
    link = Column(String)

    # METADATA
    action_metadata = Column(JSONB, server_default="{}")

    dep_extra_owner_id = Column(Integer, ForeignKey("User.id"))

    # TYPE
    type = Column(String)

    @declared_attr
    def __mapper_args__(self):
        if has_inherited_table(self):
            return {"polymorphic_identity": self.__name__[:-7]}
        return {"polymorphic_on": self.type}

    # USER RELATIONSHIPS
    members = relationship(
        "User", secondary=lambda: Action_Member_Association.__table__, cascade="all, delete"
    )
    supervisor = relationship("User", foreign_keys=[supervisor_id])

    @property
    def member_ids(self):
        return [x.id for x in self.members]

    @member_ids.setter
    def member_ids(self, ids):
        from app import crud

        self.members = crud.user.get_kw(self.db, id=ids)

    # OTHER RELATIONSHIPS
    workgroups = relationship("Workgroup", secondary=lambda: Workgroup_Action_Association.__table__)
    general_attachments = relationship(
        "Action_Attachment", back_populates="action", cascade="all,delete"
    )
    comments = relationship("Action_Comment", back_populates="action", cascade="all,delete")

    is_deleted = Column(Boolean, default=False)


class SAP_Notification_Action(Action):
    pass


class SAP_Work_Order_Action(Action):
    pass


class BMS_ACT_Action(Action):
    pass


class BMS_CR_Action(Action):
    pass


class BMS_HZD_Action(Action):
    pass


class BMS_ITR_Action(Action):
    pass


class SMH_Action(Action):
    pass


class AHM_Action(Action):
    pass


class ACE_Action(Action):
    pass


class DEP_Action(Action):
    pass


class Teams_Action(Action):
    pass
