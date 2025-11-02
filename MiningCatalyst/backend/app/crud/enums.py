from app import schemas

from .base import CRUD_Base


class Status(CRUD_Base[schemas.Status]):
    pass


class Priority(CRUD_Base[schemas.Priority]):
    pass


class Trigger(CRUD_Base[schemas.Trigger]):
    pass


class PrimaryDriver(CRUD_Base[schemas.PrimaryDriver]):
    pass


class SecondaryDriver(CRUD_Base[schemas.SecondaryDriver]):
    pass


class CostBenefitCategory(CRUD_Base[schemas.CostBenefitCategory]):
    pass


class BenefitFrequency(CRUD_Base[schemas.BenefitFrequency]):
    pass


status = Status()
priority = Priority()
trigger = Trigger()
primary_driver = PrimaryDriver()
secondary_driver = SecondaryDriver()
cost_benefit_category = CostBenefitCategory()
benefit_frequency = BenefitFrequency()
