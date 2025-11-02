# from .workgroup import Workgroup_Basic
from datetime import datetime

from app.schemas.enums import PriorityEnum, PrivacyEnum, StatusEnum, SystemTypeEnum

from .attachment import General_Attachment
from .base import Archive_Details, Base, BaseID, Datetime_Filter
from .comment import Action_Comment

# -----------------------------------------
# Associations
# -----------------------------------------


class Action_Member_Association(BaseID):
    action_id: int = None
    user_id: int = None


# -----------------------------------------
# Main
# -----------------------------------------


class Workgroup_Basic(BaseID):
    title: str = None
    privacy: PrivacyEnum = None
    owner_id: int = None
    is_active: bool = None


# class Action(Action_Basic):
#     general_attachments: list[General_Attachment] = []
#     comments: list[Action_Comment] = []
#     workgroups: list[Workgroup_Basic] = []
#     member_associations: list[Action_Member_Association] = []


class Action_Title(Base):
    id: int = None
    title: str = None
    privacy: PrivacyEnum = None


class Actions_Filters(Base):
    my_ace: bool = None
    my_team: bool = None
    my_groups: bool = None
    global_text: str = None

    workgroup_ids: list[int] = []
    title_and_description: str = None
    source_systems: list[str] = None
    owner_member_ids: list[int] = None
    date_due: Datetime_Filter = None
    status: list[StatusEnum] = []
    priority: list[PriorityEnum] = []
    functional_location: list[str] = None
    workcenters: list[str] = None
    supervisor_ids: list[int] = []
    start_date: Datetime_Filter = None
    privacy: list[PrivacyEnum] = []
    completed: list[int] = None

    archive_status: int = None


# -----------------------------------------------------------


class Base_Action(BaseID, Archive_Details):
    # base action fields
    source_id: str = None
    type: str = None
    privacy: PrivacyEnum = None
    title: str = None
    description: str = None
    priority: PriorityEnum = None
    status: StatusEnum = None
    functional_location: str = None
    work_center: str = None
    link: str = None
    date_due: datetime = None
    owner_id: int = None
    completed: int = None

    dep_extra_owner_id: int = None

    # other action fields
    member_ids: list[int] = None
    supervisor_id: int = None
    start_date: datetime = None
    date_closed: datetime = None

    is_deleted: bool = None


class Action(Base_Action):
    action_metadata: dict = {}
    general_attachments: list[General_Attachment] = []
    comments: list[Action_Comment] = []
    workgroups: list[Workgroup_Basic] = []
