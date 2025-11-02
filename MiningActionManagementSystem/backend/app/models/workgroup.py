from app.schemas.enums import PrivacyEnum

from .action import Action
from .attachment import General_Attachment
from .base import Archive_Details, Base, BaseID, Datetime_Filter
from .comment import Action_Comment

# -----------------------------------------
# Associations
# -----------------------------------------


class Workgroup_Action_Association(BaseID):
    workgroup_id: int = None
    action_id: int = None


class Workgroup_Member_Association(BaseID):
    workgroup_id: int = None
    user_id: int = None


class Workgroup_Admin_Association(BaseID):
    workgroup_id: int = None
    user_id: int = None


# -----------------------------------------
# Main
# -----------------------------------------


class Workgroup(BaseID, Archive_Details):
    # required fields
    title: str = None
    description: str = None

    owner_id: int = None
    member_ids: list[int] = None
    admin_ids: list[int] = None

    # optional fields
    functional_location: str = None
    is_active: bool = None
    privacy: PrivacyEnum = None

    # other
    general_attachments: list[General_Attachment] = []
    comments: list[Action_Comment] = []
    action_meta: object = None


class Workgroup_Full(Workgroup):
    # selected actions
    action_ids: list[int] = []
    actions: list[Action] = []


class Workgroup_Title(Base):
    id: int = None
    title: str = None
    privacy: PrivacyEnum = None


class Workgroup_Filters(Base):
    global_text: str = None
    my_groups: bool = None

    title_and_description: str = None
    owner_members_admins_ids: list[int] = []
    functional_location: list[str] = []
    date_created: Datetime_Filter = None
    date_updated: Datetime_Filter = None
    privacy: list[PrivacyEnum] = []
