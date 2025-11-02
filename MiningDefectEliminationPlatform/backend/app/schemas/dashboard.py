from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship

from .base import Base, IntEnum, StrEnum, TZDateTime
from .enums import DashboardColorEnum, DashboardTypeEnum, SiteEnum


class Team(Base):
    parent_id = Column(Integer, ForeignKey("Team.id", ondelete="CASCADE"))
    name = Column(String)
    color = Column(StrEnum(DashboardColorEnum))

    @declared_attr
    def parent(cls):
        return relationship(
            "Team",
            foreign_keys=[cls.parent_id],
            remote_side=[cls.id],
            uselist=False,
            backref=backref("children", uselist=True),
        )


class Aplus_Circuit_Association(Base):
    dashboard_id = Column(Integer, ForeignKey("Dashboard.id", ondelete="CASCADE"))
    aplus_circuit = Column(String)


class Dashboard(Base):
    # meta
    location_id = Column(Integer, ForeignKey("Team.id"))
    title = Column(String)
    tab_title = Column(String)
    tab_number = Column(Integer)
    tab_type = Column(IntEnum(DashboardTypeEnum))

    # tableau info
    tableau_url = Column(String)

    # APLUS info
    aplus_date_range = Column(String)
    aplus_site = Column(StrEnum(SiteEnum))
    aplus_area = Column(String)

    aplus_circuits = relationship("Aplus_Circuit_Association", cascade="all, delete-orphan")

    # REMS info
    rems_date_range = Column(String)
    rems_site = Column(StrEnum(SiteEnum))
    rems_fleet_type = Column(String)

    # threshold
    threshold_5_why = Column(Integer)
