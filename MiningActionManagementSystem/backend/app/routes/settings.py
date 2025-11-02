from fastapi import APIRouter, Body, Depends

from app import crud, schemas, utils

router = APIRouter()


@router.get("", response_model=utils.Settings)
def get_settings(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_SUPER_USER):
    return utils.get_settings()


@router.post("")
def edit_settings(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_SUPER_USER,
    settings: utils.Settings = Body(...),
):
    return utils.edit_settings(settings)
