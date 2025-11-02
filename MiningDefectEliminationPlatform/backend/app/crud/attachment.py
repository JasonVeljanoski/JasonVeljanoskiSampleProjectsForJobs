from app import schemas
from app.models.attachment import General_Attachment

from .base import CRUD_Base


class Attachment(CRUD_Base[schemas.Attachment]):
    pass


class General_Attachment(CRUD_Base[schemas.General_Attachment]):
    pass


class Flash_Report_Attachment(CRUD_Base[schemas.Flash_Report_Attachment]):
    pass


class Shared_Learning_Attachment(CRUD_Base[schemas.Shared_Learning_Attachment]):
    pass


attachment = Attachment()
general_attachment = General_Attachment()
flash_report_attachment = Flash_Report_Attachment()
shared_learning_attachment = Shared_Learning_Attachment()
