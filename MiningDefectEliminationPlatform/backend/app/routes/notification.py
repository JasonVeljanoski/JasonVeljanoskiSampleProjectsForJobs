from fastapi import APIRouter, Depends
from app import crud, utils, models, schemas, email, sockets

router = APIRouter()


# ------------------
# CREATE
# ------------------

# ------------------
# READ
# ------------------
@router.get("/all", response_model=list[models.Notification])
def get_notifications(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN):
    return crud.notification.get_notifications_by_user(db, user_id=user.id)


# ------------------
# DELETE
# ------------------
@router.delete("/all")
def delete_all_notifications(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    for notification in user.notifications:
        notification.is_deleted = True

    db.commit()


@router.delete("/{id}")
def delete_notification(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int = None,
):
    notification = crud.notification.get(db, id)

    if notification.user_id != user.id:
        raise utils.errors.CannotDeleteNotification

    notification.is_deleted = True
    db.commit()
