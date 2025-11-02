from __future__ import annotations

from datetime import datetime
from typing import Generic, List, TypeVar

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel


class Base(BaseModel):
    class Config:
        orm_mode = True

    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class BaseID(Base):
    id: int = None
    created: datetime = None
    updated: datetime = None


# ------------------------------
# Shared classes
# ------------------------------

T = TypeVar("T")


class PaginationResult(GenericModel, Generic[T]):
    items: list[T] = []
    count: int


class Datetime_Filter(Base):
    min_date: datetime = None
    max_date: datetime = None


class Archive_Details(Base):
    archive_user_id: int = None
    archive_datetime: datetime = None
    is_archived: bool = None
