from app.schemas.enums import FeedbackReason, FeedbackStatusEnum

from .attachment import General_Attachment
from .base import Base, BaseID, Datetime_Filter

from typing import Any


class Feedback_Comment(BaseID):
    user_id: int = None
    comment: str = None


class Feedback(BaseID):
    reason: int = None
    title: str = None
    page: str = None
    summary: str = None
    replicate: str = None
    created_by_id: int = None
    updated_by_id: int = None

    filenames: list[str] = []

    status: FeedbackStatusEnum = None
    closure_notes: str = None
    comments: list[Feedback_Comment] = []
    general_attachments: list[General_Attachment] = []


# -----------------------------------------------------------

# to make create/update work with sending attachments and its metadata (attachments suck...)
class General_Attachment_Meta(BaseID):
    title: str = None
    description: str = None
    network_drive_link: str = None


class Feedback_With_Attachments(Feedback):
    noEmail: Any = None
    general_attachments_metas: list[General_Attachment_Meta] = []


# -----------------------------------------------------------


class Feedback_Filters(Base):
    global_text: str = None
    id: int = None
    reason: list[int] = []
    created_date: Datetime_Filter = None
    updated_date: Datetime_Filter = None
    summary: str = None
    owner_id: list[int] = None
    status: list[FeedbackStatusEnum] = None
