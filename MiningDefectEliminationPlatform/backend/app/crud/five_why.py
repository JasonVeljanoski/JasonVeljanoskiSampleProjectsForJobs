from app import schemas
from app.models.five_why import Five_Why_Owner_Association
from .base import CRUD_Base


class Five_Why_Owner_Association(CRUD_Base[schemas.Five_Why_Owner_Association]):
    pass


class Five_Why(CRUD_Base[schemas.Five_Why]):
    sub_cruds = ["owners"]


class Five_Why_Response(CRUD_Base[schemas.Five_Why_Response]):
    pass


five_why_owner_association = Five_Why_Owner_Association()
five_why = Five_Why()
five_why_response = Five_Why_Response()
