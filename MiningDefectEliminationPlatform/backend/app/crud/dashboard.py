from app import schemas
from .base import CRUD_Base


class Team(CRUD_Base[schemas.Team]):
    pass


class Dashboard(CRUD_Base[schemas.Dashboard]):
    pass


team = Team()
dashboard = Dashboard()
