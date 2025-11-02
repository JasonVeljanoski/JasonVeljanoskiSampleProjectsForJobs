from re import L

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship

from .base import Base, TZDateTime


class Attachment(Base):
    five_why_response_id = Column(
        Integer,
        ForeignKey("Five_Why_Response.id", ondelete="CASCADE"),
    )
    flash_report_id = Column(
        Integer,
        ForeignKey("Flash_Report.id", ondelete="CASCADE"),
    )
    root_cause_detail_id = Column(
        Integer,
        ForeignKey("Root_Cause_Detail.id", ondelete="CASCADE"),
    )
    shared_learning_id = Column(
        Integer,
        ForeignKey("Shared_Learning.id", ondelete="CASCADE"),
    )
    action_id = Column(
        Integer,
        ForeignKey("Action.id", ondelete="CASCADE"),
    )
    filename = Column(String)
    extension = Column(String)

    # investigation = relationship(
    #     "Investigation", back_populates="actions", foreign_keys=[investigation_id]
    # )
    five_why_response = relationship(
        "Five_Why_Response", back_populates="attachments", foreign_keys=[five_why_response_id]
    )
    flash_report = relationship(
        "Flash_Report", back_populates="attachments", foreign_keys=[flash_report_id]
    )
    action = relationship("Action", back_populates="attachments", foreign_keys=[action_id])
    root_cause_detail = relationship(
        "Root_Cause_Detail", back_populates="attachments", foreign_keys=[root_cause_detail_id]
    )
    shared_learning = relationship(
        "Shared_Learning", back_populates="attachments", foreign_keys=[shared_learning_id]
    )


class General_Attachment(Base):
    title = Column(String)
    description = Column(String)
    network_drive_link = Column(String)
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
            return {"polymorphic_identity": self.__name__[:-11].replace("_", " ")}
        return {"polymorphic_on": self.type}

    @property
    def extension(self):
        return self.filename.split(".")[-1]

    # ---------------------------------


class Distribution_List_Attachment(General_Attachment):
    is_active_list = Column(Boolean, default=False) 
    # it doesn't need an item_id but just fit for the general updaload function
    @property
    def item_id(self):
        return self
  
    @item_id.setter
    def item_id(self, value):
        pass


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

    action = relationship("Action", back_populates="general_attachments", foreign_keys=[action_id])


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


class Investigation_Attachment(General_Attachment):
    investigation_id = Column(
        Integer,
        ForeignKey("Investigation.id", ondelete="CASCADE"),
    )

    @property
    def item_id(self):
        return self.investigation_id

    @item_id.setter
    def item_id(self, value):
        self.investigation_id = value

    investigation = relationship(
        "Investigation", back_populates="general_attachments", foreign_keys=[investigation_id]
    )


class Dashboard_Attachment(General_Attachment):
    dashboard_id = Column(
        Integer,
        ForeignKey("Dashboard.id", ondelete="CASCADE"),
    )
    is_active = Column(Boolean, default=False)

    @property
    def item_id(self):
        return self.dashboard_id

    @item_id.setter
    def item_id(self, value):
        self.dashboard_id = value


class Flash_Report_Attachment(General_Attachment):
    flash_report_id = Column(
        Integer,
        ForeignKey("Flash_Report.id", ondelete="CASCADE"),
    )
    is_selected_flash_report = Column(Boolean, default=False)

    @property
    def item_id(self):
        return self.flash_report_id

    @item_id.setter
    def item_id(self, value):
        self.flash_report_id = value


class Shared_Learning_Attachment(General_Attachment):
    shared_learning_id = Column(
        Integer,
        ForeignKey("Shared_Learning.id", ondelete="CASCADE"),
    )
    is_selected_shared_learning = Column(Boolean, default=False)

    @property
    def item_id(self):
        return self.shared_learning_id

    @item_id.setter
    def item_id(self, value):
        self.shared_learning_id = value
