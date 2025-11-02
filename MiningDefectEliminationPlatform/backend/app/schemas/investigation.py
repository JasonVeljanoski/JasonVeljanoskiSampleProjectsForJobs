import base64
import json
from email.policy import default
from functools import cached_property

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, column_property, relationship

from app import redis, schemas

from .base import Base, IntEnum, StrEnum, TZDateTime
from .enums import EventTypeEnum, InvestigationTypeEnum, PriorityEnum, StatusEnum
from .shared_classes import __Archive_Details__


class APLUS_Selected_Event_Details_Association(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    event_id = Column(Integer)


class REMS_Selected_Event_Details_Association(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    event_id = Column(String)


class Investigation_Owner_Association(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


class Relevant_Investigation_Association(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    relevent_investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))


# -----------------------------------------------------------


class Flash_Report(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    # event_datetime = Column(TZDateTime)
    event_title = Column(String)
    event_description = Column(String)
    business_impact = Column(String)
    immediate_action_taken = Column(String)
    potential_root_causes = Column(ARRAY(String))
    sufficient_inventory_levels = Column(Boolean)

    # custom report fields
    use_custom_report = Column(Boolean)
    custom_report_fname = Column(String)

    investigation = relationship("Investigation", back_populates="flash_report")
    actions = relationship("Action", back_populates="flash_report", cascade="all,delete-orphan")
    # potential_root_causes = relationship("Potential_Root_Cause", back_populates="flash_report")
    attachments = relationship("Attachment", back_populates="flash_report", cascade="all,delete")

    # event_datetime = association_proxy("investigation", "event_datetime")
    # event_description = association_proxy("investigation", "description")

    @property
    def files(self):
        # get all file names
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.flash_report_id == self.id)
            .all()
        )

        filenames = [x[0] for x in items]

        # get all files
        BASE64_META = "data:image/jpeg;base64,"
        files = []
        for file in filenames:
            path = f"{schemas.ImgPath.FLASH_REPORT.value}/{file}"

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
            .filter(schemas.Attachment.flash_report_id == self.id)
            .all()
        )

        return [x[0] for x in items]


# -----------------------------------------------------------


class Root_Cause_Detail(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    cause_code = Column(String)
    description = Column(String)
    additional_contribution_factors = Column(String)
    cause_category = Column(String)

    investigation = relationship("Investigation", back_populates="root_cause_detail")
    actions = relationship(
        "Action", back_populates="root_cause_detail", cascade="all,delete-orphan"
    )
    attachments = relationship(
        "Attachment", back_populates="root_cause_detail", cascade="all,delete"
    )

    # -----------------------
    complete_rca_fname = Column(String)
    # -----------------------

    @property
    def rca_filename(self):
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(
                schemas.Attachment.root_cause_detail_id == self.id,
                schemas.Attachment.extension == ".docx",
            )
            .all()
        )

        res = [x[0] for x in items]
        return res[0] if res else None


# -----------------------------------------------------------


class Shared_Learning(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    event_title = Column(String)
    event_description = Column(String)
    reason = Column(String)
    shared_learning = Column(String)
    use_custom_report = Column(Boolean)
    custom_report_fname = Column(String)

    investigation = relationship("Investigation", back_populates="shared_learning")
    attachments = relationship("Attachment", back_populates="shared_learning", cascade="all,delete")

    @property
    def initiative_images(self):
        # get all file names
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.shared_learning_id == self.id)
            .all()
        )

        filenames = [x[0] for x in items]

        # get all files
        BASE64_META = "data:image/jpeg;base64,"
        files = []
        for file in filenames:
            path = f"{schemas.ImgPath.SHARED_LEARNING.value}/{file}"

            try:
                with open(path, "rb") as f:
                    b64_slug = base64.b64encode(f.read()).decode("ascii")
                    base_64_string = f"{BASE64_META}{b64_slug}"
                    files.append(base_64_string)
            except Exception:
                pass

        return files

    @property
    def initiative_image_filenames(self):
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.shared_learning_id == self.id)
            .all()
        )

        return [x[0] for x in items]


# -----------------------------------------------------------


class Investigation(Base, __Archive_Details__):

    # CREATE NEW INVESTIGATION [form] ------------
    # INVESTIGATION DETAILS
    title = Column(String)
    description = Column(String)
    priority = Column(StrEnum(PriorityEnum))
    investigation_type = Column(IntEnum(InvestigationTypeEnum))

    event_datetime = Column(TZDateTime)
    completion_due_date = Column(TZDateTime)
    date_closed = Column(TZDateTime)
    working_folder_link = Column(String)

    steps_completed = Column(Integer)

    has_completed_rca = Column(Boolean, default=False)

    # EQUIPMENT DETAILS
    # snowflake values - must be hard coded due to unreliable ids
    # floc_ids are not unique

    # -------------------------------------------

    function_location = Column(String)
    equipment_description = Column(String)

    @property
    def site(self):
        return self.equipment_info.get("site", None)

    @property
    def department(self):
        return self.equipment_info.get("department", None)

    @cached_property
    def equipment_info(self):
        redis_db = redis.get_redis()

        info = redis_db.get(f"{self.function_location}_{self.equipment_description}")

        redis_db.close()

        if not info:
            return {}

        info = json.loads(info)

        return info

    # -------------------------------------------

    object_type = Column(String)
    catalog_profile = Column(String)
    catalog_profiles = Column(ARRAY(String))
    object_part_description = Column(String)
    damage_code = Column(String)

    supervisor_id = Column(Integer, ForeignKey("User.id"))
    event_type = Column(IntEnum(EventTypeEnum))
    status = Column(IntEnum(StatusEnum))

    # -------------------------------------------

    total_effective_duration = Column(Float)
    total_tonnes_lost = Column(Float)
    total_event_duration = Column(Float)

    # -------------------------------------------

    cause_code = Column(String)

    # -------------------------------------------

    supervisor = relationship("User", foreign_keys=[supervisor_id])
    owners = relationship("Investigation_Owner_Association", cascade="all, delete-orphan")
    owner_users = relationship("User", secondary=lambda: Investigation_Owner_Association.__table__)

    @property
    def owner_ids(self):
        return [x.user_id for x in self.owners]

    # EVENT DETAILS
    aplus_delay_events = relationship(
        "APLUS_Selected_Event_Details_Association", cascade="all, delete-orphan"
    )
    rems_delay_events = relationship(
        "REMS_Selected_Event_Details_Association", cascade="all, delete-orphan"
    )

    @property
    def aplus_delay_event_ids(self):
        return [x.event_id for x in self.aplus_delay_events]

    @property
    def rems_delay_event_ids(self):
        return [x.event_id for x in self.rems_delay_events]

    # -------------------------------------------

    # ROOT CAUSE
    # cause = Column(String)

    # RELEVANT INVESTIGATIONS ------------
    # Super-cool self-referential many-to-many relationship
    @declared_attr
    def relevant_investigations(cls):
        return relationship(
            "Investigation",
            secondary=lambda: Relevant_Investigation_Association.__table__,
            primaryjoin=(Relevant_Investigation_Association.investigation_id == cls.id),
            secondaryjoin=(Relevant_Investigation_Association.relevent_investigation_id == cls.id),
            backref=backref("investigation_id", lazy="select"),
            lazy="select",
        )

    @property
    def relevant_investigation_ids(self):
        return [x.id for x in self.relevant_investigations]

    # -----------------------------------

    # OTHER RELATIONSHIPS ------------
    flash_report = relationship("Flash_Report", back_populates="investigation", uselist=False)
    five_why = relationship("Five_Why", back_populates="investigation", uselist=False)
    shared_learning = relationship("Shared_Learning", back_populates="investigation", uselist=False)
    actions = relationship("Action", back_populates="investigation")
    root_cause_detail = relationship(
        "Root_Cause_Detail", back_populates="investigation", uselist=False
    )
    general_attachments = relationship(
        "Investigation_Attachment", back_populates="investigation", cascade="all,delete"
    )

    @property
    def actions_number(self):
        return len(self.actions)

    # ---------------------------------
