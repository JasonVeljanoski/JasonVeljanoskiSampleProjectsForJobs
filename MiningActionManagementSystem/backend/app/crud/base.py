import datetime as dt
from typing import Any, Generic, Type, TypeVar, get_args

import pytz
import sqlalchemy.orm as sql_orm
from sqlalchemy.orm import Session

from app.models.base import Base as Models_Base
from app.schemas.base import Base as Schemas_Base

# --------------------------------
#  TRY NOT TO REMOVE ANY METHODS!
# --------------------------------


class Comparator(object):
    value: Any
    op: callable = None


T = TypeVar("T")


class CRUD_Base(Generic[T]):
    schema: Type[T] = None
    sub_objs = {}
    sub_cruds = []

    prevent_updates = []

    def __init__(self):
        self.schema = get_args(self.__orig_bases__[0])[0]

    def all(self, db: Session, limit=None, order_by=None) -> list[T]:
        query = db.query(self.schema).order_by(order_by or self.order_key)

        if limit:
            return query.limit(limit).all()
        else:
            return query.all()

    def get(self, db: Session, id: int) -> T:
        db_obj = db.query(self.schema).filter(self.schema.id == id).first()
        return db_obj

    def get_all(self, db: Session, ids: list) -> list[T]:
        return [db.query(self.schema).filter(self.schema.id == id).first() for id in ids]

    def get_kw(self, db: Session, order_by=None, **filters) -> list[T]:
        query = db.query(self.schema)

        query = self.__add_filters__(db, query, filters)

        order_by = order_by or self.order_key

        return query.order_by(order_by).all()

    def get_kw_single(self, db: Session, **filters) -> T:
        db_obj = self.get_kw(db, **filters)

        if len(db_obj) > 1:
            raise ValueError("There were multiple found")
        elif len(db_obj) == 0:
            db_obj = None
        else:
            db_obj = db_obj[0]

        return db_obj

    def get_distinct(self, db, column, **filters):
        query = db.query(column).order_by(column)

        query = self.__add_filters__(db, query, filters.copy())

        return [x for x, in query.distinct()]

    def get_page(self, db: Session, page, count, sort_by=["id"], sort_desc=[True], **filters):
        query = db.query(self.schema)

        query = self.__add_sorting__(query, sort_by, sort_desc)

        query = self.__add_filters__(db, query, filters)

        return dict(items=query.limit(count).offset((page - 1) * count).all(), count=query.count())

    def count(self, db: Session, **filters) -> int:
        query = db.query(self.schema)

        query = self.__add_filters__(db, query, filters)

        return query.count()

    def get_create(self, db: Session, **kwargs) -> T:
        obj = self.get_kw_single(db, **kwargs)

        if not obj:
            obj = self.create(db, self.schema(**kwargs))

        return obj

    def create(self, db: Session, obj) -> T:

        # TODO support raw dicts

        if isinstance(obj, Models_Base):
            obj = self.update(db, obj)
        elif isinstance(obj, Schemas_Base):
            db.add(obj)
            db.commit()
            db.refresh(obj)
        else:
            raise Exception("I dont know what this is")

        return obj

    def update_all(self, db: Session, edits: list, commit=True) -> list[T]:
        return [self.update(db, x, commit) for x in edits]

    def update(self, db: Session, edits, commit=True, level=0) -> T:

        if isinstance(edits, Schemas_Base):
            raise Exception("Schemas do not use the update function. Just db.commit()....")

        if isinstance(edits, Models_Base):
            edits = edits.dict(exclude_unset=True)

        if "id" not in edits or not edits["id"]:
            obj = self.schema()
            db.add(obj)
        else:
            obj = self.get(db, edits["id"])
            if not obj:
                raise ValueError("Cannot find entry to update")

        for k, v in edits.items():
            if k == "id" or k.startswith("_") or k in self.prevent_updates:
                continue

            try:
                field = getattr(self.schema, k)
            # It its a field
            except AttributeError:
                continue

            field_type = type(field)

            # Sqlalchemy field type
            if field_type == sql_orm.attributes.InstrumentedAttribute:
                property_type = type(field.property)
                # Its a column
                if property_type == sql_orm.properties.ColumnProperty:
                    setattr(obj, k, v)
                # Its a relationship
                elif property_type == sql_orm.properties.RelationshipProperty:
                    from app import crud

                    if k not in self.sub_cruds:
                        continue

                    temp = field.property

                    class_ = temp.argument
                    if type(class_) == sql_orm.Mapper:
                        class_ = class_.class_.__name__

                    sub_crud = getattr(crud, class_.lower())

                    # Other table has the foreign key
                    if temp.direction == sql_orm.relationships.ONETOMANY:
                        sub_items = [
                            sub_crud.update(db, x, commit=False, level=level + 1) for x in v
                        ]
                        setattr(obj, k, sub_items)

                    # This table has the foreign key
                    elif temp.direction == sql_orm.relationships.MANYTOONE:
                        # to_be_added = "id" not in v or not v["id"]
                        sub_item = sub_crud.update(db, v, commit=False, level=level + 1)
                        setattr(obj, k, sub_item)

            # Its a property but has a setter
            # elif field_type == sql_ext.associationproxy.ColumnAssociationProxyInstance:
            #     pass
            elif field.fset:
                setattr(obj, k, v)

        if commit:
            db.commit()
            db.refresh(obj)

        return obj

    def duplicate(self, db: Session, id, **overrides) -> T:
        obj = self.get(db, id)

        if not obj:
            return None

        data = {}

        for col in obj.__table__.columns:
            if col.name != self.schema.id:
                data[col.name] = getattr(obj, col.name)

        for k, v in overrides.items():
            data[k] = v

        new_obj = obj.__class__(**data)

        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)

        return new_obj

    def delete(self, db: Session, id: int):
        deleted = db.query(self.schema).filter(self.schema.id == id).delete()
        db.commit()

        return deleted

    def delete_kw(self, db: Session, in_memory=True, **filters):
        query = db.query(self.schema)

        query = self.__add_filters__(db, query, filters)

        if in_memory:
            deleted = query.all()
            for item in deleted:
                db.delete(item)
        else:
            deleted = query.delete()
        db.commit()

        return deleted

    def delete_all(self, db: Session, reset=False, in_memory=True):

        deleted = self.delete_kw(db, in_memory=in_memory)

        if reset and self.schema.__tablename__:
            db.execute(f'ALTER SEQUENCE "{self.schema.__tablename__}_id_seq" RESTART WITH 1')

        db.commit()
        return deleted

    # ----------------------------------------------------------------------------------------------------

    @property
    def order_key(self):
        return self.schema.id

    # ----------------------------------------------------------------------------------------------------

    def __add_filters__(self, db: Session, query, filters):

        for k, v in filters.items():
            query = self.__add_filter__(db, query, k, v)

        return query

    def __add_filter__(self, db: Session, query, field, value):
        col = getattr(self.schema, field)

        if type(value) in [list, set]:
            query = query.filter(col.in_(value))
        else:
            query = query.filter(col == value)

        return query

    def __add_sorting__(self, query, sort_by=["id"], sort_desc=[True]):
        orders = []
        for by, desc in zip(sort_by, sort_desc):
            col = getattr(self.schema, by)
            if desc:
                col = col.desc()
            orders.append(col)

        orders.append(self.schema.id.desc())

        if orders:
            query = query.order_by(*orders)

        return query


def add_date_filter(query, field, column, filters):
    if field in filters:

        min_date = filters[field]["min_date"]
        max_date = filters[field]["max_date"]

        if min_date:
            query = query.filter(column >= min_date - dt.timedelta(days=1))
        if max_date:
            query = query.filter(column < max_date)

        del filters[field]

    return query


# ----------------------------------------------------------------------------------------------------


class Rule(Models_Base):
    type: str
    value: str = None


class Rules(Models_Base):
    field: str
    mode: str
    rules: list[Rule]


def __convert_str_datetime(x):

    if x.endswith("Z"):
        x = x[:-1]

    x = dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
    return pytz.timezone("Australia/Perth").localize(x)


def __equals__(x, y):
    if not y:
        return x.is_(None)

    return x == y if y.isnumeric() else x.ilike(f"{y}")


RULE_SQL = dict(
    starts_with=lambda x, y: x.ilike(f"{y}%") if y else x.ilike("%"),
    ends_with=lambda x, y: x.ilike(f"%{y}") if y else x.ilike("%"),
    contains=lambda x, y: x.ilike(f"%{y}%") if y else x.ilike("%"),
    does_not_contain=lambda x, y: ~x.ilike(f"%{y}%") if y else ~x.ilike("%"),
    equals=lambda x, y: __equals__(x, y),
    does_not_equal=lambda x, y: ~__equals__(x, y),
    is_greater_than=lambda x, y: x > y,
    is_less_than=lambda x, y: x < y,
    date_equals=lambda x, y: x == __convert_str_datetime(y) if y else x.is_(None),
    is_after=lambda x, y: x > __convert_str_datetime(y) if y else x.is_(None),
    is_before=lambda x, y: x < __convert_str_datetime(y) if y else x.is_(None),
    is_true=lambda x, y: x.is_(True),
    is_false=lambda x, y: x.is_(False),
    is_empty=lambda x, y: x.is_(None),
    is_not_empty=lambda x, y: x.isnot(None),
)
