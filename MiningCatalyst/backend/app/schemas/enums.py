import enum

from sqlalchemy.orm import backref, relationship

from .base import Base
from .shared_classes import __ENUM__, __Deletable__


class InitiativeTypeEnum(enum.StrEnum):
    GENERAL_IMPROVEMENT = "general_improvement"
    NON_FLOC_SPECIFIC = "non_floc_specific"
    MAINTENANCE_IMPROVEMENT = "maintenance_improvement"
    MAINTENANCE_PROJECT = "maintenance_project"
    COST_REDUCTION = "cost_reduction"
    SAFETY = "safety"
    CAPITAL = "capital"


# ------------------------------------------------------------


class Status(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class Priority(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class PrimaryDriver(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class SecondaryDriver(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class Trigger(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class BenefitFrequency(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


class CostBenefitCategory(Base, __ENUM__, __Deletable__):
    @property
    def order_key(self):
        if self.order is not None:
            return self.order
        return self.id


# ------------------------------------------------------------
