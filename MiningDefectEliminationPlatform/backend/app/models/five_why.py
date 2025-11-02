from .action import Action
from .base import BaseID


class Five_Why_Owner_Association(BaseID):
    five_why_id: int = None
    user_id: int = None


class Five_Why(BaseID):
    investigation_id: int = None
    root_response_id: int = None
    event_description: str = None
    owner_ids: list[int] = []
    supervisor_id: int = None
    is_complete: bool = False
    flash_report_action_ids: list[int] = []
    # event_datetime: datetime = None
    # supervisor_id: int = None


class Five_Why_Response(BaseID):
    parent_response_id: int = None
    cause: str = None
    reason: str = None
    files: list[str] = []
    filenames: list[str] = []


# class Five_Why_Participants(Base):
#     id: int = None
#     five_why_id: int = None
#     user: str = None  # user_id: int = None


class Five_Why_Response_Full(Five_Why_Response):
    children_responses: "list[Five_Why_Response_Full]" = []


class Five_Why_Full(Five_Why):
    root_response: Five_Why_Response_Full = []
    actions: list[Action] = []
    owners: list[Five_Why_Owner_Association] = []
    # participants: list[Five_Why_Participants] = []
