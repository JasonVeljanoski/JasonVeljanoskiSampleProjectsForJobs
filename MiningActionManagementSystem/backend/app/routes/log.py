import json
from datetime import datetime
from typing import Union

from app import crud, email, models, schemas, utils
from app.schemas.enums import PrivacyEnum
from fastapi import APIRouter, Body, Depends, File, UploadFile
from html_sanitizer import Sanitizer

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("/create_history", response_model=models.Update_History)
def create_history(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_ADMIN,
    content: str,
):
    sanitizer = Sanitizer()
    content = sanitizer.sanitize(content)
    # Deactivate all other histories
    db.query(schemas.Update_History).update({"active": False})
    db.commit()

    return crud.update_history.create(db, schemas.Update_History(user_id=user.id, content=content))


# ------------------
# READ
# ------------------
@router.get("/get_logs")
def get_logs(*, db=Depends(utils.get_db), valid=Depends(utils.token_auth)):
    return crud.log.all(db)


@router.get("/latest_update", response_model=models.Update_History)
def get_latest_update(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return db.query(schemas.Update_History).order_by(schemas.Update_History.created.desc()).first()


@router.get("/history", response_model=list[models.Update_History])
def get_history(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.update_history.all(db)


# ------------------
# UPDATE
# ------------------
@router.put("/update_history_activate")
def update_history_activate(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_ADMIN,
    id: int,
    active: bool,
):
    # Deactivate all other histories
    if active:
        db.query(schemas.Update_History).update({"active": False})

    # Activate the selected history
    db.query(schemas.Update_History).filter(schemas.Update_History.id == id).update(
        {"active": active}
    )

    # Reset the "dont show again" flag for each user
    db.query(schemas.User).update({"dont_show_news_again": False})

    db.commit()


@router.patch("/update_history/dont_show_again")
def update_history_dont_show_again(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    db.query(schemas.User).filter(schemas.User.id == user.id).update({"dont_show_news_again": True})
    db.commit()
