from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from .base import Base, StrEnum, TZDateTime
from .enums import InitiativeTypeEnum


class InitiativeTrigger(Base):
    trigger_id = Column(Integer, ForeignKey("trigger.id", ondelete="CASCADE"))
    initiative_id = Column(Integer, ForeignKey("initiative.id", ondelete="CASCADE"))


class Initiative(Base):
    # -------------------------- SHARED ---------------------------

    # FOREIGN KEYS
    parent_initiative = Column(Integer, ForeignKey("initiative.id"))

    # TYPE
    type = Column(StrEnum(InitiativeTypeEnum), nullable=False)

    # GENERAL
    date_opened = Column(TZDateTime)
    target_completion_date = Column(TZDateTime)
    title = Column(String)
    description = Column(String)

    # USERS
    project_owner_id = Column(Integer, ForeignKey("user.id"))
    supervisor_id = Column(Integer, ForeignKey("user.id"))

    # ENUMS
    priority_id = Column(Integer, ForeignKey("priority.id"))
    priority = relationship("Priority", backref=backref("initiatives", lazy="dynamic"))

    status_id = Column(Integer, ForeignKey("status.id"))
    status = relationship("Status", backref=backref("initiatives", lazy="dynamic"))

    # OTHER
    change_request = Column(String)

    # -------------------------- GENERAL IMPROVEMENT ---------------------------

    # BENEFIT
    tonnes = Column(Integer)
    safety = Column(Integer)
    availability = Column(Integer)
    events = Column(Integer)
    benefit_estimate_notes = Column(String)

    # SCHEDULE
    notification = Column(String)
    workorder = Column(String)

    # ORGANISATIONAL UNITS
    impact_ou_id = Column(Integer, ForeignKey("organisational_unit.id"))
    owner_ou_id = Column(Integer, ForeignKey("organisational_unit.id"))

    # ENUMS
    triggers = relationship(
        "Trigger",
        secondary=lambda: InitiativeTrigger.__table__,
        cascade="all, delete",
    )

    primary_driver_id = Column(Integer, ForeignKey("primary_driver.id"))
    primary_driver = relationship("PrimaryDriver", backref=backref("initiatives", lazy="dynamic"))

    secondary_driver_id = Column(Integer, ForeignKey("secondary_driver.id"))
    secondary_driver = relationship(
        "SecondaryDriver", backref=backref("initiatives", lazy="dynamic")
    )

    cost_benefit_category_id = Column(Integer, ForeignKey("cost_benefit_category.id"))
    cost_benefit_category = relationship(
        "CostBenefitCategory", backref=backref("initiatives", lazy="dynamic")
    )

    benefit_frequency_id = Column(Integer, ForeignKey("benefit_frequency.id"))
    benefit_frequency = relationship(
        "BenefitFrequency", backref=backref("initiatives", lazy="dynamic")
    )

    @property
    def trigger_ids(self):
        return [x.id for x in self.triggers]

    @trigger_ids.setter
    def trigger_ids(self, ids):
        from app import schemas

        with self.db.no_autoflush:
            triggers = self.db.query(schemas.Trigger).filter(schemas.Trigger.id.in_(ids)).all()
            self.triggers = triggers

    # -------------------------- NON FLOC SPECIFIC ---------------------------

    floc_id = Column(Integer, ForeignKey("floc.id"))
    equipment_id = Column(Integer, ForeignKey("equipment.id"))

    # -------------------------- MAINTENANCE IMPROVEMENT --------------------------

    maintenance_plan = Column(String)

    # -------------------------- MAINTENANCE PROJECT --------------------------

    cost = Column(Float)
    purchase_request = Column(String)
    purchase_order = Column(String)
