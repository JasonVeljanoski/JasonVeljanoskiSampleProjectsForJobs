from app import schemas
from .base import CRUD_Base


class Log(CRUD_Base[schemas.Log]):
    pass


log = Log()
