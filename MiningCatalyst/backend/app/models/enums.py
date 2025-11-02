from .base import Base


class EnumRead(Base):
    id: int = None
    label: str
    order: int = None
    order_key: int = None
    color: str = None


class EnumWrite(Base):
    id: int = None
    label: str
    order: int = None
    color: str = None


# ------------------------------------------------------------


class AllEnumsRead(Base):
    priority: list[EnumRead]
    status: list[EnumRead]
    trigger: list[EnumRead]
    primary_driver: list[EnumRead]
    secondary_driver: list[EnumRead]
    cost_benefit_category: list[EnumRead]
    benefit_frequency: list[EnumRead]
