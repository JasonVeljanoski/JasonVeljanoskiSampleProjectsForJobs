from datetime import datetime

from .base import BaseID


class Attachment(BaseID):
    five_why_response_id: int = None
    flash_report_id: int = None
    root_cause_detail_id: int = None
    action_id: int = None
    feedback_id: int = None

    filename: str = None


class General_Attachment(BaseID):
    title: str = None
    description: str = None
    network_drive_link: str = None
    unique_filename: str = None
    filename: str = None
    size: int = None
    extension: str = None
    uploaded_by: int = None
    deleted: bool = None
    deleted_date: datetime = None
    deleted_by: int = None
    is_active: bool = None
    is_active_list: bool = None
