import base64
import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app import schemas, utils

from .base import Base, IntEnum, StrEnum, TZDateTime
from .enums import PriorityEnum, StatusEnum
from .shared_classes import __Archive_Details__, __Deletable__


class Historical(enum.IntEnum):
    NOT_HISTORICAL = 0
    HISTORICAL = 1


class Action_Owner_Association(Base):
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


class Action_Member_Association(Base):
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


class Action_Comment(Base):
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id"))
    comment = Column(String)
    action = relationship("Action", foreign_keys=[action_id], back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])


class Action(Base, __Archive_Details__, __Deletable__):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    five_why_id = Column(Integer, ForeignKey("Five_Why.id", ondelete="CASCADE"))
    flash_report_id = Column(Integer, ForeignKey("Flash_Report.id", ondelete="CASCADE"))
    root_cause_detail_id = Column(Integer, ForeignKey("Root_Cause_Detail.id", ondelete="CASCADE"))
    title = Column(String)
    description = Column(String)
    priority = Column(StrEnum(PriorityEnum))
    date_due = Column(TZDateTime)
    date_closed = Column(TZDateTime)
    supervisor_id = Column(Integer, ForeignKey("User.id"))
    status = Column(IntEnum(StatusEnum))

    is_historical = Column(IntEnum(Historical), default=Historical.NOT_HISTORICAL)

    is_archived = Column(Boolean, default=False)

    investigation = relationship(
        "Investigation", back_populates="actions", foreign_keys=[investigation_id]
    )
    five_why = relationship("Five_Why", back_populates="actions", foreign_keys=[five_why_id])
    flash_report = relationship(
        "Flash_Report", back_populates="actions", foreign_keys=[flash_report_id]
    )
    root_cause_detail = relationship(
        "Root_Cause_Detail", back_populates="actions", foreign_keys=[root_cause_detail_id]
    )
    # root_cause_detail = relationship(
    #     "Root_Cause_Detail", back_populates="actions", foreign_keys=[root_cause_detail_id]
    # )
    comments = relationship("Action_Comment", back_populates="action", cascade="all,delete")
    attachments = relationship("Attachment", back_populates="action", cascade="all,delete")
    general_attachments = relationship(
        "Action_Attachment", back_populates="action", cascade="all,delete"
    )

    supervisor = relationship("User", foreign_keys=[supervisor_id])

    owners = relationship("Action_Owner_Association", cascade="all, delete")
    owner_users = relationship("User", secondary=lambda: Action_Owner_Association.__table__)

    @property
    def owner_ids(self):
        return [x.user_id for x in self.owners]

    members = relationship("Action_Member_Association", cascade="all, delete")
    member_users = relationship("User", secondary=lambda: Action_Member_Association.__table__)

    @property
    def member_ids(self):
        return [x.user_id for x in self.members]

    # -------------------------------------------------
    # images

    @property
    def files(self):
        # get all file names
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.action_id == self.id)
            .all()
        )

        filenames = [x[0] for x in items]

        # get all files
        BASE64_META = "data:image/jpeg;base64,"
        files = []
        for file in filenames:
            path = f"{utils.ImgPath.ACTION.value}/{file}"

            try:
                with open(path, "rb") as f:
                    b64_slug = base64.b64encode(f.read()).decode("ascii")
                    base_64_string = f"{BASE64_META}{b64_slug}"
                    files.append(base_64_string)
            except Exception:
                pass

        return files

    @property
    def filenames(self):
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.action_id == self.id)
            .all()
        )

        return [x[0] for x in items]

    # -------------------------------------------------
    # investigation

    @property
    def investigation_title(self):
        # get investigation title
        if self.investigation:
            return self.investigation.title
        return None

    @property
    def investigation_description(self):
        # get investigation description
        if self.investigation:
            return self.investigation.description
        return None

    # @property
    # def investigation_site(self):
    #     # get investigation site
    #     if self.investigation:
    #         return self.investigation.site
    #     return None

    # @property
    # def investigation_department(self):
    #     # get investigation department
    #     if self.investigation:
    #         return self.investigation.department
    #     return None

    @property
    def investigation_owner_ids(self):
        # # get investigation owners
        investigation_owner_ids = self.investigation.owner_ids

        # get investigation supervisor
        investigation_supervisor_id = self.investigation.supervisor_id

        # return list containing investigation owners ids + supervisor id for this action
        if (
            investigation_supervisor_id
            and investigation_supervisor_id not in investigation_owner_ids
        ):
            investigation_owner_ids.append(investigation_supervisor_id)

        return investigation_owner_ids

    # -------------------------------------------------
