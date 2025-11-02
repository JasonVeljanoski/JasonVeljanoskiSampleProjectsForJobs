from datetime import datetime

from .base import Base, BaseID


class User(BaseID):
    name: str = None
    email: str = None
    access: int = None
    location_id: int = None
    supervisor_id: int = None


class User_Full(BaseID):
    name: str = None
    email: str = None
    access: int = None
    job_title: str = None
    location_id: int = None
    team_name: str = None
    is_user: bool = None
    last_logged_in: datetime = None


class WatchedGroups(Base):
    sites: list[str] = None
    departments: list[str] = None
    object_types: list[str] = None
    show_all: bool = False


class CurrentUser(User_Full):
    watched_groups: WatchedGroups = WatchedGroups()


class User_Filters(BaseID):
    user: str = None
