import datetime as dt

from .base import Base, BaseID


class Fmg_Employees(Base):
    sap_number: int = None  # employee_BK
    key_employee_supervisor: int = None
    first_name: str = None
    last_name: str = None
    email: str = None
    full_name: str = None


class User_Basic(BaseID):
    name: str = None
    email: str = None
    supervisor_id: int = None
    dont_show_news_again: bool = None


class User(BaseID):
    name: str = None
    email: str = None
    job_title: str = None
    microsoft_id: str = None
    sap_number: int = None
    # access: str = None
    access: int = None
    last_logged_in: dt.datetime = None
    role: str = None
    functional_locations: list[str] = None
    work_centers: list[str] = None
    site: str = None
    back_to_back_email: str = None
    txoilsample: bool = None
    dont_show_news_again: bool = None

    # ---

    back_to_back_id: int = None
    back_to_back: Fmg_Employees = None
    supervisor_id: int = None


class User_Edit(Base):
    """Eventually remove after refactor//Currently being used but will require a better way"""

    id: int = None
    name: str = None
    email: str = None
    sap_number: int = None
    access: int = None
    functional_loc: str = None
    work_center: str = None
    job_title: str = None
    last_logged_in: dt.datetime = None
    is_user: bool = False


class Users_Filters(Base):
    # Search string
    global_text: str = None

    id: int = None
    # Things to filter the string by
    name: str = None
    email: str = None
    job_title: str = None


class User_Logged_In:
    userId: int = None
    access_token: str = None
    refresh_token: str = None
    timestamp = dt.datetime

    def __init__(self, userId, access_token, refresh_token, timestamp):
        self.userId = userId
        self.access_token = access_token
        self.refresh_token = refresh_token

        if(isinstance(timestamp, str)):
            self.timestamp = dt.datetime.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp