from .base import BaseID


# class Damage_Code(Base):
#     id: int = None
#     code: str = None
#     description: str = None
#     type: str = None


# class Cause_Code(Base):
#     id: int = None
#     code: str = None
#     description: str = None
#     type: str = None


class Equipment(BaseID):
    function_location: str = None
    catalog_profile: str = None
    equipment_description: str = None
    object_type: str = None
    site: str = None
    department: str = None


# class Object_Part(Base):
#     id: int = None
#     code: str = None
#     description: str = None
#     type: str = None


class Object_Code(BaseID):
    cat_prof_code: str = None
    cat_prof_description: str = None
    catalog: str = None
    code_group: str = None
    code_group_description: str = None
    object_code: str = None
    object_description: str = None
