import datetime as dt

from .base import BaseID

from app.schemas.enums import DashboardColorEnum, DashboardTypeEnum, SiteEnum


class Team(BaseID):
    parent_id: int = None
    name: str = None
    color: DashboardColorEnum = None

    children: "list[Team]" = []


class Aplus_Circuit_Association(BaseID):
    dashboard_id: int = None
    aplus_circuit: str = None


class Dashboard(BaseID):
    title: str = None
    tab_title: str = None
    tab_number: int = None
    tab_type: DashboardTypeEnum = None

    tableau_url: str = None

    threshold_5_why: int = None

    aplus_date_range: str = None
    aplus_site: SiteEnum = None
    aplus_area: str = None
    aplus_circuits: list[Aplus_Circuit_Association] = []

    rems_date_range: str = None
    rems_site: SiteEnum = None
    rems_fleet_type: str = None
