from datetime import datetime
from typing import Union
from xmlrpc.client import Boolean

from app import crud, email, models, schemas, utils
from app.schemas.enums import PrivacyEnum
from app.schemas.user import Access
from fastapi import APIRouter, Body, Depends

router = APIRouter()


# ------------------
# CREATE
# ------------------

# ------------------
# READ
# ------------------
@router.get("/action_titles", response_model=list[models.Action_Title])
def get_action_titles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.action.get_action_titles(db, user)


@router.get("/workgroup_titles", response_model=list[models.Workgroup_Title])
def get_workgroup_titles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.workgroup.get_workgroup_titles(db, user)


# ------------------
# UPDATE
# ------------------

# ------------------
# DELETE
# ------------------
