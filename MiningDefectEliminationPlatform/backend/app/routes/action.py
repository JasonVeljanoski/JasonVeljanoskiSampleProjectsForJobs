import datetime as dt
import json

from fastapi import APIRouter, Body, Depends, File, UploadFile

from app import crud, models, schemas, utils
from app.crud import notification
from app.models.base import Base
from app.schemas import PriorityEnum, StatusEnum

router = APIRouter()

# ------------------
# READ
# ------------------

# ------------------
# CREATE
# ------------------
@router.post("/get_page", response_model=models.PaginationResult[models.Action])
def get_action_page(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: models.Actions_Filters = Body(None),
):
    filters = filters.dict(exclude_unset=True)
    filters["user_id"] = user.id

    return crud.action.get_page(db, page, count, sort_by, sort_desc, **filters)


@router.get("", response_model=list[models.Action])
def get_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    action_id: int,
):
    return crud.action.get_kw(db, id=action_id)


@router.get("/all_actions")
def get_all_actions(
    *, db=Depends(utils.get_db), valid=Depends(utils.token_auth), last_updated: dt.datetime = None
):
    # TODO: Check API key

    filters = [
        "a.is_archived is not True",
        """(
            a.is_historical = 1 or
            coalesce(a.five_why_id, a.flash_report_id, a.root_cause_detail_id) is not Null
        )""",
    ]

    if last_updated:
        # ! this might not work. also wont filter on nested updated
        filters.append(f"a.updated >= '{last_updated}'")

    return db.execute(
        f"""
        select
            a.id,
            a.created,
            a.updated,
            a.investigation_id,
            i.function_location as functional_location,
            a.title,
            a.description,
            a.status,
            a.priority,
            a.date_due,
            a.date_closed,
            super.email as supervisor_email,
            (
                select array_agg(o.email)
                from "Action_Owner_Association" aoa
                left join "User" o on o.id = aoa.user_id
                where aoa.action_id = a.id
            ) as owner_emails,
            (
                select array_agg(m.email)
                from "Action_Member_Association" ama
                left join "User" m on m.id = ama.user_id
                where ama.action_id = a.id
            ) as member_emails
        from "Action" a
        left join "Investigation" i on i.id = a.investigation_id
        left join "User" super on super.id = a.supervisor_id
        where {' and '.join(filters)}
        order by a.updated
    """
    ).fetchall()


@router.get("/all_action_ids")
def all_action_ids(*, db=Depends(utils.get_db), valid=Depends(utils.token_auth)):
    res = db.query(schemas.Action.id).all()

    return [x.id for x in res]


@router.get("/investigation_id", response_model=list[models.Action])
def get_action_from_investigation(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    investigation_id: int,
):
    return crud.action.get_kw(db, investigation_id=investigation_id)


@router.get("/user_open", response_model=list[models.Action])
def get_user_actions(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.action.get_user_open_actions(db, user_id=user.id)


# ------------------
# UPDATE
# ------------------
@router.put("", response_model=models.Action)
def update_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action: str = Body(...),
    attachments: list[UploadFile] = File(...),
):
    edits = models.Action_With_Attachments(**json.loads(action))
    file_metadatas = edits.genertal_attachments_metas

    # GET OLD OWNERS/SUPERVISOR
    _old = crud.action.get(db, edits.id)
    old_owners = []
    if _old:
        old_owners = old_owners + _old.owner_ids
        old_owners.append(_old.supervisor_id)

    # ------------------
    # IMAGE UPLOAD

    action = crud.action.update(db, edits)
    action.attachments = utils.create_upload_files(
        edits.files, utils.ImgPath.ACTION.value, base_name="action", suffix="jpeg"
    )

    # ------------------
    # GENERAL ATTACHMENTS UPLOAD

    if attachments:
        utils.upload_attachments(
            db, schemas.Action_Attachment, action.id, user, attachments, file_metadatas
        )

    # ------------------
    # LOGGING

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            action_id=action.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.ACTION,
        ),
    )

    # ------------------

    db.commit()
    db.refresh(action)

    # ------------------
    # BROADCAST ALERT

    # send notifications for linked actions only
    # ! this is a risk point (if we add actions somethere else, this is a dependency that needs to change)
    if action.flash_report_id or action.five_why_id:
        if not edits.noEmail:
            utils.broadcast_action_alert(db, action.id, old_owners, edits.id == None)

    # ------------------

    return action


@router.patch("/add_comment", response_model=models.Action_Comment)
def add_comment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action_id: int,
    comment: str,
):

    res = crud.action_comment.create(
        db,
        schemas.Action_Comment(
            action_id=action_id,
            user_id=user.id,
            comment=comment,
        ),
    )

    # -----------------------------------------------

    # update every users action via socket layer
    utils.broadcast_action_update_socket(db, action_id)

    # general notification to this user
    utils.create_notification(
        db,
        user.id,
        "Comment Added",
        f"New comment added for action #{action_id}",
        tags=[],
        status="success",
    )

    # -----------------------------------------------

    return res


@router.patch("/update_archive_status")
def update_archive_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action_id: int,
    is_archived: bool,
):
    if action_id:
        db.query(schemas.Action).filter(schemas.Action.id == action_id).update(
            {
                "is_archived": is_archived,
                "archive_user_id": user.id,
                "updated": utils.get_time_now(),
                "archive_datetime": utils.get_time_now(),
            }
        )
        db.commit()
