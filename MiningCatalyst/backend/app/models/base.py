import datetime as dt

from pydantic import BaseModel, validator


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
    created: dt.datetime = None
    updated: dt.datetime = None
