from fastapi import APIRouter, Depends
from sqlalchemy.orm import aliased

from app import crud, models, schemas, utils

router = APIRouter()


@router.post("/equipment", response_model=list[models.Equipment])
def from_flocs_get_equipment(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN, floc_ids: list[int] = []
):
    floc_alias = aliased(schemas.Floc)

    cte = (
        db.query(schemas.Equipment)
        .select_from(schemas.Floc)
        .join(schemas.Floc.equipment)
        .filter(schemas.Floc.id.in_(floc_ids))
        .cte(recursive=True)
    )

    children = cte.union_all(
        db.query(schemas.Equipment)
        .select_from(schemas.Floc)
        .join(schemas.Floc.equipment)
        .filter(schemas.Floc.parent_id == floc_alias.id)
        .filter(cte.c.id == floc_alias.parent_id)
    ).select()

    return db.execute(children).fetchall()


@router.get("", response_model=list[models.Floc])
def get_flocs(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN, search: str = None
):
    if search is None or len(search) <= 2:
        return []

    return db.query(schemas.Floc).filter(schemas.Floc.node.ilike(f"%{search}%")).all()
