from app import schemas
from .base import CRUD_Base


# class Damage_Code(CRUD_Base[schemas.Damage_Code]):
#     pass


# class Cause_Code(CRUD_Base[schemas.Cause_Code]):
#     pass


# class Object_Part(CRUD_Base[schemas.Object_Part]):
#     pass


class Equipment(CRUD_Base[schemas.Equipment]):
    pass


class Object_Code(CRUD_Base[schemas.Object_Code]):
    pass


# cause_code = Cause_Code()
# damage_code = Damage_Code()
# object_part = Object_Part()
equipment = Equipment()
object_code = Object_Code()
