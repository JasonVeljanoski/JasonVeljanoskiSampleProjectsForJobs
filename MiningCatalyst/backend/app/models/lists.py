from .base import Base


class OrganisationalUnit(Base):
    id: int
    area: str
    department: str = None
    section: str = None


class Equipment(Base):
    id: int
    functional_location: str
    equipment: str
