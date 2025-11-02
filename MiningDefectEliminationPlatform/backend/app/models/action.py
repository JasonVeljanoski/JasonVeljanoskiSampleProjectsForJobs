from datetime import datetime

from app.schemas.enums import ActionSourceEnum, PriorityEnum, StatusEnum

from .attachment import General_Attachment
from .base import Base, BaseID, Datetime_Filter


class Action_Owner_Association(BaseID):
    action_id: int = None
    user_id: int = None


class Action_Member_Association(BaseID):
    action_id: int = None
    user_id: int = None


class Action_Comment(BaseID):
    user_id: int = None
    comment: str = None


class Action(BaseID):
    investigation_id: int = None
    investigation_title: str = None
    investigation_description: str = None
    five_why_id: int = None
    flash_report_id: int = None
    root_cause_detail_id: int = None
    title: str = None
    description: str = None
    status: StatusEnum = None
    priority: PriorityEnum = None
    date_due: datetime = None
    date_closed: datetime = None
    supervisor_id: int = None
    is_archived: bool = None
    is_deleted: bool = None
    owner_ids: list[int] = []
    member_ids: list[int] = []
    files: list[str] = []
    filenames: list[str] = []
    investigation_owner_ids: list[int] = []
    owners: list[Action_Owner_Association] = []
    members: list[Action_Member_Association] = []
    general_attachments: list[General_Attachment] = []
    comments: list[Action_Comment] = []


# -----------------------------------------------------------

# to make create/update work with sending attachments and its metadata (attachments suck...)
class General_Attachment_Meta(BaseID):
    title: str = None
    description: str = None
    network_drive_link: str = None


class Action_With_Attachments(Action):
    noEmail: bool = None
    genertal_attachments_metas: list[General_Attachment_Meta] = []


# -----------------------------------------------------------


class Action_Ace(BaseID):
    id: int = None
    investigation_id: int = None
    investigation_title: str = None
    investigation_description: str = None
    title: str = None
    description: str = None
    status: StatusEnum = None
    priority: PriorityEnum = None
    date_due: datetime = None
    date_closed: datetime = None
    # supervisor_id: int = None
    # is_archived: bool = None
    # owner_ids: list[int] = []
    # investigation_owner_ids: list[int] = []
    # owners: list[Action_Owner_Association] = []

    owner_emails: list[str] = []
    investigation_owner_emails: list[str] = []
    supervisor_email: str = None


# -------------------------------------------------


class Actions_Filters(Base):
    show_mine: bool = None
    global_text: str = None

    id: int = None
    site: list[str] = None
    department: list[str] = None
    function_location: list[str] = None
    status: list[StatusEnum] = []
    priority: list[PriorityEnum] = []
    source: list[ActionSourceEnum] = []
    title: str = None

    date_due: Datetime_Filter = None
    date_closed: Datetime_Filter = None
    created_date: Datetime_Filter = None
    updated_date: Datetime_Filter = None

    supervisor_id: list[int] = []
    owner_member_ids: list[int] = []
    member_ids: list[int] = []

    archive_status: int = None
