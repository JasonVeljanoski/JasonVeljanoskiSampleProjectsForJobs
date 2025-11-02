import datetime as dt
import enum
import re

import pytz
from sqlalchemy import Column, DateTime, Integer, MetaData, String
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import as_declarative, declared_attr, has_inherited_table
from sqlalchemy.orm import object_session
from sqlalchemy.types import TypeDecorator


class __CustomType__(TypeDecorator):
    cache_ok = True

    def __repr__(self) -> str:
        return self.impl.__repr__()


class LowercaseString(__CustomType__):
    impl = String()
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.lower()
        return value


class TZDateTime(__CustomType__):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            # If its a string, convert it
            if isinstance(value, str):
                value = dt.datetime.fromisoformat(value[:-1]).replace(tzinfo=pytz.UTC)

            # If there is no timezone then assume that it belongs in Perth
            if not value.tzinfo:
                value = pytz.timezone("Australia/Perth").localize(value)
            else:
                value = value.astimezone(pytz.timezone("Australia/Perth"))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.astimezone(pytz.timezone("Australia/Perth"))

        return value


class __Enum__(__CustomType__):
    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if value is not None:
            try:
                if isinstance(value, enum.Enum):
                    value = value.value
            except Exception as e:
                print("Enum error:", e)
                pass

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = self.enumtype(value)
        return value


class IntEnum(__Enum__):
    impl = Integer

    cache_ok = True


class StrEnum(__Enum__):
    impl = String

    cache_ok = True


# ------------------------------------------------------------------------------

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        # "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


def __get_time__():
    from app import utils

    return utils.get_time_now()


@as_declarative(metadata=meta)
class Base(object):
    id = Column(Integer, primary_key=True, index=True)

    created = Column(TZDateTime, default=__get_time__, nullable=False)
    updated = Column(TZDateTime, default=__get_time__, nullable=False)

    __attr_exclude__ = []
    __attr_include__ = []

    @declared_attr
    def __tablename__(self):
        if has_inherited_table(self):
            return None

        return re.sub("(?!^)([A-Z]+)", r"_\1", self.__name__).lower()

    def to_dict(self):
        return {key: getattr(self, key) for key in self.__get_attrs__()}

    @property
    def db(self):
        return object_session(self)

    def __get_attrs__(self):
        return [
            c.name
            for c in self.__table__.columns
            if not c.name.startswith("_") and c.name != "id" and c.name not in self.__attr_exclude__
        ] + self.__attr_include__

    def __str__(self) -> str:
        attrs = filter(lambda x: x != "id", self.__get_attrs__())
        values = ", ".join([f"id={self.id}"] + [f"{x}={getattr(self, x,'??')}" for x in attrs])

        return f"{type(self).__name__}({values})"

    def __repr__(self) -> str:
        return self.__str__()


@listens_for(Base, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target: Base):
    target.updated = __get_time__()
