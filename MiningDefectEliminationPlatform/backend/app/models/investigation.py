from datetime import datetime
from typing import Any

from app.schemas.enums import EventTypeEnum, InvestigationTypeEnum, PriorityEnum, StatusEnum

from .action import Action
from .attachment import General_Attachment
from .base import Base, BaseID, Datetime_Filter
from .five_why import Five_Why_Full
from .user import User


class Investigation_Owner_Association(BaseID):
    investigation_id: int = None
    user_id: int = None


class Relevant_Investigation_Association(BaseID):
    investigation_id: int = None
    relevent_investigation_id: int = None


class APLUS_Selected_Event_Details_Association(BaseID):
    investigation_id: int = None
    event_id: int = None


class REMS_Selected_Event_Details_Association(BaseID):
    investigation_id: int = None
    event_id: str = None


# -----------------------------------------------------------


class Email(BaseID):
    users: list[str] = []
    message: str = None


class Flash_Report_Email(Email):
    path: str = None


# -----------------------------------------------------------


class Flash_Report(BaseID):
    investigation_id: int = None
    event_title: str = None
    event_description: str = None
    business_impact: str = None
    immediate_action_taken: str = None
    potential_root_causes: list[str] = []
    sufficient_inventory_levels: bool = None

    # TODO ----------- needed?
    aplus_delay_event_ids: list[int] = []
    # rems_delay_event_ids: list[str] = []
    # TODO -----------

    actions: list[Action] = []
    files: list[str] = []
    filenames: list[str] = []
    # attachments: list[str] = []
    # attachment_names: list[str] = []
    use_custom_report: bool = None
    custom_report_fname: str = None


# -----------------------------------------------------------


class Root_Cause_Detail(BaseID):
    investigation_id: int = None
    cause_code: str = None  # should be fk ref
    description: str = None
    additional_contribution_factors: str = None
    cause_category: str = None  # should be an ENUM
    files: list[str] = []
    filenames: list[str] = []
    actions: list[Action] = []

    # ! needed ? -----
    rca_doc: object = None
    rca_filename: str = None
    # ! ---------------

    complete_rca_fname: str = None


# -----------------------------------------------------------


class Shared_Learning(BaseID):
    investigation_id: int = None
    event_title: str = None
    event_description: str = None
    reason: str = None
    shared_learning: str = None
    use_custom_report: bool = None
    custom_report_fname: str = None
    initiative_images: list[str] = []
    initiative_image_filenames: list[str] = []


# -----------------------------------------------------------


class Investigation_Title(Base):
    id: int = None
    title: str = None


# -----------------------------------------------------------


class Investigation_Light(BaseID):
    # CREATE NEW INVESTIGATION [form] ------------
    # INVESTIGATION DETAILS
    title: str = None
    description: str = None
    priority: PriorityEnum = None
    investigation_type: InvestigationTypeEnum = None
    working_folder_link: str = None
    actions_number: int = None

    # EQUIPMENT DETAILS
    # snowflake values - must be hard coded due to unreliable ids
    # floc_ids are not unique
    function_location: str = None
    catalog_profile: str = None
    catalog_profiles: list[str] = []
    object_part_description: str = None
    damage_code: str = None
    equipment_description: str = None
    object_type: str = None
    site: str = None
    department: str = None
    owner_ids: list[int] = []
    supervisor_id: int = None

    status: StatusEnum = None
    date_closed: datetime = None

    # EVENT DETAILS
    aplus_delay_event_ids: list[int] = []
    rems_delay_event_ids: list[str] = []
    event_datetime: datetime = None
    completion_due_date: datetime = None
    event_type: EventTypeEnum = None

    total_effective_duration: float = None
    total_tonnes_lost: float = None
    total_event_duration: float = None
    has_completed_rca: bool = None

    cause_code: str = None
    # -------------------------------------------

    is_archived: bool = None
    # -----------------------


# -----------------------------------------------------------


class Investigation(BaseID):
    # CREATE NEW INVESTIGATION [form] ------------
    # INVESTIGATION DETAILS
    title: str = None
    description: str = None
    priority: PriorityEnum = None
    investigation_type: InvestigationTypeEnum = None
    working_folder_link: str = None
    actions_number: int = None

    # EQUIPMENT DETAILS
    # snowflake values - must be hard coded due to unreliable ids
    # floc_ids are not unique
    function_location: str = None
    catalog_profile: str = None
    catalog_profiles: list[str] = []
    object_part_description: str = None
    damage_code: str = None
    equipment_description: str = None
    object_type: str = None
    site: str = None
    department: str = None
    owner_ids: list[int] = []
    supervisor_id: int = None

    status: StatusEnum = None
    date_closed: datetime = None

    # EVENT DETAILS
    aplus_delay_event_ids: list[int] = []
    rems_delay_event_ids: list[str] = []
    event_datetime: datetime = None
    completion_due_date: datetime = None
    event_type: EventTypeEnum = None

    total_effective_duration: float = None
    total_tonnes_lost: float = None
    total_event_duration: float = None

    cause_code: str = None
    # -------------------------------------------

    # ROOT CAUSE
    # ! remove from schemas as well
    # cause: str = None

    # RELEVANT INVESTIGATIONS ------------
    relevant_investigation_ids: list[int] = []
    # ------------------------------------

    # OTHER META ------------
    steps_completed: int = None
    is_archived: bool = None
    # -----------------------

    # MINIMUM REQUIREMENTS
    general_attachments: list[General_Attachment] = []
    owners: list[Investigation_Owner_Association] = []
    root_cause_detail: Root_Cause_Detail = None
    shared_learning: Shared_Learning = None


# -----------------------------------------------------------


class Investigation_Full(Investigation):
    aplus_delay_events: list[APLUS_Selected_Event_Details_Association] = []
    rems_delay_events: list[REMS_Selected_Event_Details_Association] = []
    # owners: list[Investigation_Owner_Association] = []
    owner_users: list[User] = []
    relevant_investigations: list[Investigation] = []
    five_why: Five_Why_Full = None
    flash_report: Flash_Report = None
    # root_cause_detail: Root_Cause_Detail = None
    actions: list[Action] = []
    workorders: list[str] = []


# -----------------------------------------------------------

# to make create/update work with sending attachments and its metadata (attachments suck...)
class General_Attachment_Meta(BaseID):
    title: str = None
    description: str = None
    network_drive_link: str = None


class Investigation_With_Attachments(Investigation_Full):
    noEmail: Any = None
    genertal_attachments_metas: list[General_Attachment_Meta] = []


# -----------------------------------------------------------


class Investigations_Filters(Base):
    show_mine: bool = None
    global_text: str = None

    id: int = None
    title: str = None
    status: list[StatusEnum] = []
    priority: list[PriorityEnum] = []
    function_location: list[str] = []
    investigation_type: list[InvestigationTypeEnum] = []

    incident_date: Datetime_Filter = None
    date_closed: Datetime_Filter = None
    updated_date: Datetime_Filter = None
    created_date: Datetime_Filter = None
    completion_due_date: Datetime_Filter = None
    completed_steps: list[int] = []

    supervisor_id: list[int] = []
    owner_ids: list[int] = []

    site: list[str] = []
    department: list[str] = []
    equipment_description: list[str] = []
    object_type: list[str] = []
    object_part_description: list[str] = []
    damage_code: list[str] = []
    causes: list[str] = []

    effective_duration: list[float] = []
    event_duration: list[float] = []

    blacklist_ids: list[int] = []
    show_relevant_flag: bool = None
    investigation_id: int = None

    archive_status: int = None
    is_archive: bool = None
