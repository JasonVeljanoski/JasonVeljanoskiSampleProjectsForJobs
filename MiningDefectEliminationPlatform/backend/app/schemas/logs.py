from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

from app import utils, schemas
from .base import Base, StrEnum, TZDateTime, IntEnum
from .enums import LogEnum


class Log(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    flash_report_id = Column(Integer, ForeignKey("Flash_Report.id", ondelete="CASCADE"))
    five_why_id = Column(Integer, ForeignKey("Five_Why.id", ondelete="CASCADE"))
    root_cause_detail_id = Column(Integer, ForeignKey("Root_Cause_Detail.id", ondelete="CASCADE"))
    shared_learning_id = Column(Integer, ForeignKey("Shared_Learning.id", ondelete="CASCADE"))
    action_id = Column(Integer, ForeignKey("Action.id", ondelete="CASCADE"))

    # ------------------------------

    user_id = Column(Integer, ForeignKey("User.id"))
    log_type = Column(StrEnum(LogEnum))
