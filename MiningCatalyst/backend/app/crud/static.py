from app import schemas

from .base import CRUD_Base


class OrganisationalUnit(CRUD_Base[schemas.OrganisationalUnit]):
    pass


class Equipment(CRUD_Base[schemas.Equipment]):
    pass


class Floc(CRUD_Base[schemas.Floc]):
    pass


organisational_unit = OrganisationalUnit()
equipment = Equipment()
floc = Floc()
