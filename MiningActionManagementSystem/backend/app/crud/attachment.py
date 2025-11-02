from app import schemas
from .base import CRUD_Base


class General_Attachment(CRUD_Base[schemas.General_Attachment]):
    pass


general_attachment = General_Attachment()
