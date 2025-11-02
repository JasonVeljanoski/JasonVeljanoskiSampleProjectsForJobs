import datetime as dt

from app.schemas import InitiativeTypeEnum

from .base import BaseID
from .enums import EnumRead


class BaseInitiative(BaseID):
    parent_initiative_id: int = None
    parent_initiative: "BaseInitiative" = None

    type: InitiativeTypeEnum = None

    date_opened: dt.datetime = None
    target_completion_date: dt.datetime = None
    title: str = None
    description: str = None

    project_owner_id: int = None
    supervisor_id: int = None

    priority_id: int = None
    priority: EnumRead = None

    status_id: int = None
    status: EnumRead = None

    change_request: str = None


class GeneralImprovementInitiative(BaseID):
    id: int = None

    owner_ou_id: int = None
    impact_ou_id: int = None

    trigger_ids: list[int] = []
    triggers: list[EnumRead] = []

    primary_driver_id: int = None
    primary_driver: EnumRead = None

    secondary_driver_id: int = None
    secondary_driver: EnumRead = None

    cost_benefit_category_id: int = None
    cost_benefit_category: EnumRead = None

    benefit_frequency_id: int = None
    benefit_frequency: EnumRead = None

    tonnes: int = None
    safety: int = None
    availability: int = None
    events: int = None
    benefit_estimate_notes: str = None

    notification: str = None
    workorder: str = None


class NonFlocSpecificInitiative(BaseID):
    owner_ou_id: int = None
    impact_ou_id: int = None

    trigger_ids: list[int] = []
    triggers: list[EnumRead] = []

    floc_id: int = None
    equipment_id: int = None

    primary_driver_id: int = None
    primary_driver: EnumRead = None

    secondary_driver_id: int = None
    secondary_driver: EnumRead = None

    tonnes: int = None
    safety: int = None
    availability: int = None
    events: int = None
    benefit_frequency: int = None
    benefit_estimate_notes: str = None

    notification: str = None
    workorder: str = None


class MaintenanceImprovement(BaseID):
    owner_ou_id: int = None
    impact_ou_id: int = None

    trigger_ids: list[int] = []
    triggers: list[EnumRead] = []

    floc_id: int = None
    equipment_id: int = None

    maintenance_plan: str = None

    primary_driver_id: int = None
    primary_driver: EnumRead = None

    secondary_driver_id: int = None
    secondary_driver: EnumRead = None

    tonnes: int = None
    safety: int = None
    availability: int = None
    events: int = None
    benefit_frequency: int = None
    benefit_estimate_notes: str = None

    notification: str = None


class MaintenanceProject(BaseID):
    impact_ou_id: int = None

    floc_id: int = None
    equipment_id: int = None

    primary_driver_id: int = None
    primary_driver: EnumRead = None

    secondary_driver_id: int = None
    secondary_driver: EnumRead = None

    cost: float = None

    tonnes: int = None
    safety: int = None
    availability: int = None
    events: int = None
    benefit_frequency: int = None
    benefit_estimate_notes: str = None

    notification: str = None
    workorder: str = None

    purchase_request: str = None
    purchase_order: str = None


# ----------------------------------------------------------------------------------------------


class FullInitiative(
    BaseInitiative,
    GeneralImprovementInitiative,
    NonFlocSpecificInitiative,
    MaintenanceImprovement,
    MaintenanceProject,
):
    pass
