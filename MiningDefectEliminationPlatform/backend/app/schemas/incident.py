from sqlalchemy import Column, String, Integer
from .base import Base


class Equipment(Base):
    function_location = Column(String)
    catalog_profile = Column(String)
    equipment_description = Column(String)
    object_type = Column(String)
    site = Column(String)
    department = Column(String)


class Object_Code(Base):
    cat_prof_code = Column(String)
    cat_prof_description = Column(String)
    catalog = Column(String)
    code_group = Column(String)
    code_group_description = Column(String)
    object_code = Column(String)
    object_description = Column(String)
