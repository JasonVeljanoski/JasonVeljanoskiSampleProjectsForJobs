from datetime import datetime
from email.policy import default

import pytz
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.sqltypes import Boolean

from .base import Base, IntEnum, TZDateTime
from .enums import PrivacyEnum
from .shared_classes import __Archive_Details__

utc = pytz.UTC


class Workgroup(Base, __Archive_Details__):
    # ----------------------------------------------------------------------------------------
    # Fields
    # required fields
    title = Column(String)
    description = Column(String)

    owner_id = Column(Integer, ForeignKey("User.id"))

    # optional fields
    functional_location = Column(String)
    is_active = Column(Boolean, default=True)
    privacy = Column(IntEnum(PrivacyEnum), nullable=False, default=PrivacyEnum.PUBLIC)
    teams_id = Column(String)
    teams_last_updated = Column(TZDateTime)

    # ----------------------------------------------------------------------------------------
    # Comments and attachments

    comments = relationship("Workgroup_Comment", back_populates="workgroup", cascade="all,delete")
    general_attachments = relationship(
        "Workgroup_Attachment", back_populates="workgroup", cascade="all,delete"
    )

    # ----------------------------------------------------------------------------------------
    # Members

    members = relationship(
        "User", secondary=lambda: Workgroup_Member_Association.__table__, cascade="all, delete"
    )

    @property
    def member_ids(self):
        return [x.id for x in self.members]

    @member_ids.setter
    def member_ids(self, ids):
        from app import crud

        self.members = crud.user.get_kw(self.db, id=ids)

    # ----------------------------------------------------------------------------------------
    # Admins

    admins = relationship(
        "User", secondary=lambda: Workgroup_Admin_Association.__table__, cascade="all, delete"
    )

    @property
    def admin_ids(self):
        return [x.id for x in self.admins]

    @admin_ids.setter
    def admin_ids(self, ids):
        from app import crud

        self.admins = crud.user.get_kw(self.db, id=ids)

    # ----------------------------------------------------------------------------------------
    # Actions

    actions = relationship(
        "Action", secondary=lambda: Workgroup_Action_Association.__table__, cascade="all, delete"
    )

    @property
    def action_ids(self):
        return [x.id for x in self.actions]

    @action_ids.setter
    def action_ids(self, ids):
        from app import crud

        self.actions = crud.action.get_kw(self.db, id=ids)

    @property
    def action_meta(self):
        from app import schemas

        due_count = 0
        overdue_count = 0
        for action in self.actions:
            # count overdue actions
            if action.status == schemas.StatusEnum.OVERDUE:
                overdue_count += 1
                continue

            # count open actions due within a week
            if action.status != schemas.StatusEnum.OPEN:
                continue

            if action.date_due is not None:
                due = action.date_due.replace(tzinfo=utc)
                now = datetime.now().replace(tzinfo=utc)
                if (due - now).days <= 7:
                    due_count += 1

        return {
            "due_count": due_count,
            "overdue_count": overdue_count,
            "total_count": due_count + overdue_count,
        }

    # ----------------------------------------------------------------------------------------


# -----------------------------------------
# Association Tables
# -----------------------------------------
class Workgroup_Action_Association(Base):
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id", ondelete="CASCADE"))
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))


class Workgroup_Member_Association(Base):
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


class Workgroup_Admin_Association(Base):
    workgroup_id = Column(Integer, ForeignKey("Workgroup.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))
