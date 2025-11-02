from .base import Base, BaseID


class OrganisationalUnit(Base):
    id: int
    area: str = None
    department: str = None
    team: str = None


class Equipment(BaseID):
    description: str = None


class Floc(BaseID):
    node: str = None
    parent_id: int = None
    equipment_id: int = None
