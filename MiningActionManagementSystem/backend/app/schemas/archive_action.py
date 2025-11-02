from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified

from app.schemas.enums import ActionTagEnum, LinkedSystemEnum, PriorityEnum, PrivacyEnum, StatusEnum

from .base import Base, IntEnum, StrEnum, TZDateTime
from .shared_classes import __Archive_Details__

# ------------------------------------------------------------------------------------------


class Archive_Action(Base, __Archive_Details__):

    # COMMON FIELDS
    title = Column(String)
    description = Column(String)

    priority = Column(String)

    owner_email = Column(String)
    supervisor_email = Column(String)

    source_created = Column(TZDateTime)
    source_updated = Column(TZDateTime)

    action_created = Column(
        TZDateTime
    )  # Timestamp of when action record was created, 'created' in Action
    action_id = Column(Integer)

    start_date = Column(TZDateTime)
    date_due = Column(TZDateTime)

    privacy = Column(String)

    status = Column(String)

    date_closed = Column(TZDateTime)

    # ACTION TYPE
    source_id = Column(String)

    # OTHER
    completed = Column(Integer, default=0)
    functional_location = Column(String)
    work_center = Column(String)
    link = Column(String)

    # METADATA
    action_metadata = Column(String)

    dep_extra_owner_email = Column(String)

    # TYPE
    type = Column(String)

    # USER RELATIONSHIPS
    member_emails = Column(
        String
    )  # The emails of members that belonged to this action (Action_Member_Association),
    #       represented as a string comma seperated e.g. "email1@a.com,email2@a.com"

    # OTHER RELATIONSHIPS
    workgroup_titles = Column(
        String
    )  # Titles of workgroups that belonged to this action (Workgroup_Action_Association),
    #       represented as a string comma seperated e.g. "Wkgp1,Wkgp2"

    # Archive metadata - in __Archive_Details__
    """
    archive_user_id = Column(Integer)
    archive_datetime = Column(TZDateTime, nullable=True)
    is_archived = Column(Boolean, default=False)

    # Following will be set when an Action is archived:
    #   archive_action.archive_datetime = utils.get_time_now()
    #   archive_action.is_archived = 1
    """

    syncUUID = Column(String)
