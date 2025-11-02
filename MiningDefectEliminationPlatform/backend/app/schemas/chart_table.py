from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
)


from app.schemas.base import Base
from .enums import TimeUsageCode
from .base import Base, StrEnum


class Charting(Base):
    equipment_id = Column(Integer)
    equipment_name = Column(String)
    start_time = Column(DateTime)
    date = Column(Date)
    effective_duration = Column(Float)
    time_usage_code = Column(String)
    problem = Column(String)
    action = Column(String)
    cause = Column(String)
    region_name = Column(String)
    area_name = Column(String)
    circuit = Column(String)
    time_usage_code = Column(StrEnum(TimeUsageCode))

    @property
    def name_cause(self):
        if self.cause:
            return f"{self.equipment_name} {self.cause}"
        return self.equipment_name


class ChartingREMS(Base):
    event_id = Column(String)
    event_datetime = Column(DateTime)
    last_comment = Column(String)
    functional_location = Column(String)
    fleet_type = Column(String)
    model = Column(String)
    equipment_name = Column(String)
    site = Column(String)
    floc6 = Column(String)
    floc7 = Column(String)
    floc8 = Column(String)
    event_duration = Column(Float)
