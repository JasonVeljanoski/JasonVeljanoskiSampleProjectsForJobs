import base64

from app import schemas
from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship

from .base import Base, TZDateTime


class Five_Why_Owner_Association(Base):
    five_why_id = Column(Integer, ForeignKey("Five_Why.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"))


class Five_Why(Base):
    investigation_id = Column(Integer, ForeignKey("Investigation.id", ondelete="CASCADE"))
    root_response_id = Column(Integer, ForeignKey("Five_Why_Response.id", ondelete="CASCADE"))
    # action_owners_notified = Column(Boolean)
    # notification_raised = Column(Boolean)
    event_description = Column(String)
    supervisor_id = Column(Integer, ForeignKey("User.id"))
    is_complete = Column(Boolean)
    flash_report_action_ids = Column(ARRAY(Integer))
    # supervisor = Column(String)  #
    # supervisor_id = Column(Integer, ForeignKey("User.id"))
    # event_datetime = Column(TZDateTime)

    # supervisor = relationship("User", foreign_keys=[supervisor_id])  #
    # participants = relationship("Five_Why_Participants", back_populates="five_why", uselist=True)
    root_response = relationship("Five_Why_Response", back_populates="five_why", uselist=False)
    # actions = relationship("Five_Why_Action", back_populates="five_why", uselist=True)
    actions = relationship("Action", back_populates="five_why", cascade="all,delete-orphan")
    investigation = relationship("Investigation", back_populates="five_why")

    supervisor = relationship("User", foreign_keys=[supervisor_id])
    owner_users = relationship("User", secondary=lambda: Five_Why_Owner_Association.__table__)
    owners = relationship("Five_Why_Owner_Association", cascade="all, delete-orphan")

    @property
    def owner_ids(self):
        return [x.user_id for x in self.owners]


# class Five_Why_Participants(Base):
#     five_why_id = Column(Integer, ForeignKey("Five_Why.id"))
#     user_id = Column(
#         Integer, ForeignKey("User.id")
#     )  # user_id = Column(Integer, ForeignKey("User.id"))
#     user = relationship("User", back_populates="five_why_participants", foreign_keys=[user_id])
#     five_why = relationship("Five_Why", back_populates="participants", foreign_keys=[five_why_id])


class Five_Why_Response(Base):
    parent_response_id = Column(Integer, ForeignKey("Five_Why_Response.id", ondelete="CASCADE"))
    cause = Column(String)
    reason = Column(String)

    @declared_attr
    def parent_response(cls):
        return relationship(
            "Five_Why_Response",
            foreign_keys=[cls.parent_response_id],
            remote_side=[cls.id],
            uselist=False,
            backref=backref("children_responses", uselist=True),
        )

    attachments = relationship(
        "Attachment", back_populates="five_why_response", cascade="all,delete"
    )
    five_why = relationship("Five_Why", back_populates="root_response", uselist=True)

    @property
    def files(self):
        from app import utils

        # get all file names
        items = (
            self.db.query(schemas.Attachment.filename)
            .filter(schemas.Attachment.five_why_response_id == self.id)
            .all()
        )

        filenames = [x[0] for x in items]

        # get all files
        BASE64_META = "data:image/jpeg;base64,"
        files = []
        for file in filenames:
            path = f"{utils.ImgPath.FIVE_WHY.value}/{file}"

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
            .filter(schemas.Attachment.five_why_response_id == self.id)
            .all()
        )

        return [x[0] for x in items]
