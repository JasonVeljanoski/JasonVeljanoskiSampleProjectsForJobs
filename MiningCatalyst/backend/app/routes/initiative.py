from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends

from app import crud, errors, models, schemas, utils

router = APIRouter()


# ------------------
# CREATE
# ------------------
# ....


# ------------------
# READ
# ------------------
@router.get("", response_model=models.FullInitiative)
def get_initiative(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    # new initiative
    if id == -1:
        return models.FullInitiative()

    # otherwise
    return crud.initiative.get(db, id)


@router.get("/general_improvement", response_model=models.GeneralImprovementInitiative)
def get_general_improvement(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    # new initiative
    if id == -1:
        return models.GeneralImprovementInitiative()

    # otherwise
    return crud.general_improvement.get(db, id)


@router.get("/all", response_model=list[models.FullInitiative])
def get_all_initiatives(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    res = crud.initiative.all(db, order_by="updated")
    return res[::-1]


# ------------------
# UPDATE
# ------------------
@router.put("", response_model=models.FullInitiative)
def update_initiative(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    initiative: models.FullInitiative,
):
    return crud.initiative.update(db, initiative)
