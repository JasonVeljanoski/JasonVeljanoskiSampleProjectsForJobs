import datetime as dt

from .base import BaseID
from app.schemas.enums import TimeUsageCode


class Charting_chart(BaseID):
    equipment_name: str = None
    sum_duration: float = None
    equipment_count: int = None
    cause: str = None
    within_week_count: int = None
    over_week_count: int = None
    within_week_sum: float = None
    over_week_sum: float = None
    has_investigation: int = None


class Charting(BaseID):
    equipment_id: int = None
    equipment_name: str = None
    start_time: dt.datetime = None
    date: dt.date = None
    effective_duration: float = None
    problem: str = None
    action: str = None
    cause: str = None
    name_cause: str = None
    region_name: str = None
    circuit: str = None
    area_name: str = None
    time_usage_code: TimeUsageCode = None


class Charting_Table(Charting):
    ids: list = []
    sum_duration: float = None
    equipment_count: int = None
    within_a_week: bool = None


class Filter(BaseID):
    name: str = None
    count: int = None


class Time_Usage_Filter(BaseID):
    name: TimeUsageCode = None
    count: int = None


class Charting_Area(BaseID):
    area_name: str = None
    circuit: str = None
    time_usage_code: TimeUsageCode = None


class Charting_Filter(BaseID):
    problems: list[Filter] = []
    actions: list[Filter] = []
    region_names: list[Filter] = []
    area_names: list[Filter] = []
    circuits: list[Filter] = []
    time_usage_codes: list[Time_Usage_Filter] = []


class Charting_Filter_REMS(BaseID):
    sites: list[Filter] = []
    flee_types: list[Filter] = []
    models: list[Filter] = []
    floc6s: list[Filter] = []
    floc7s: list[Filter] = []
    floc8s: list[Filter] = []


class Charting_Floc_Table(BaseID):
    floc6: str = None
    floc7: str = None
    floc8: str = None
    equipment_name: str = None
    event_datetime: dt.datetime = None
    last_comment: str = None
    event_duration: float = None


class Floc_All_Items(Charting_Floc_Table):
    event_id: str = None
    functional_location: str = None
    fleet_type: str = None
    model: str = None
    equipment_name: str = None
    site: str = None


class Charting_Floc_Base(BaseID):
    floc: str = None
    duration: float = None
    name: str = None
    count: int = None


class Charting_Floc8(Charting_Floc_Base):
    floc6: str = None
    floc7: str = None


class Charting_Floc(BaseID):
    floc6: list[Charting_Floc_Base] = []
    floc7_1: list[Charting_Floc_Base] = []
    floc7_2: list[Charting_Floc_Base] = []
    floc7_3: list[Charting_Floc_Base] = []
