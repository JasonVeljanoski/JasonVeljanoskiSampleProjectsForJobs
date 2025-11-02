from app import schemas
from .base import CRUD_Base


class APLUS_Selected_Event_Details_Association(
    CRUD_Base[schemas.APLUS_Selected_Event_Details_Association]
):
    pass


class REMS_Selected_Event_Details_Association(
    CRUD_Base[schemas.REMS_Selected_Event_Details_Association]
):
    pass


class Charting(CRUD_Base[schemas.Charting]):
    pass


class ChartingREMS(CRUD_Base[schemas.ChartingREMS]):
    pass


charting_rems = ChartingREMS()
charting = Charting()
aplus_selected_event_details_association = APLUS_Selected_Event_Details_Association()
rems_selected_event_details_association = REMS_Selected_Event_Details_Association()
