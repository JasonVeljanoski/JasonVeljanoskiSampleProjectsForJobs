from fastapi import APIRouter, Depends

from app import crud, models, schemas, utils

router = APIRouter()


@router.post("/floc", response_model=list[models.Floc])
def from_equipment_get_flocs(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN, equipment_ids: list[int]
):
    return db.query(schemas.Floc).filter(schemas.Floc.equipment_id.in_(equipment_ids)).all()


@router.get("", response_model=list[models.Equipment])
def get_equipment(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN, search: str = None
):
    if search is None or len(search) <= 2:
        return []

    return (
        db.query(schemas.Equipment).filter(schemas.Equipment.description.ilike(f"%{search}%")).all()
    )
