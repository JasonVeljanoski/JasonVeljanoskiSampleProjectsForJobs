import datetime as datetime
import json

import pytz
from app import crud, email, models, schemas, utils
from app.crud import user
from app.schemas.enums import LogTypeEnum, PrivacyEnum
from app.utils.errors import PermissionDeniedException
from app.utils.security import IS_ADMIN
from fastapi import APIRouter, Body, Depends, File, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("", response_model=models.Action)
def create_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: models.Action,
):

    # new actions are ACE actions
    if not edits.id:
        edits.type = "ACE"  # specify ACE type

    # --------------------------------------------

    action = crud.action.update(db, edits)

    # --------------------------------------------
    # create action log

    crud.log.create_action_log(db, LogTypeEnum.ACTION_CREATION, user.id, action.id)

    # --------------------------------------------

    return action


@router.post("/comment")
def create_comment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action_id: int,
    comment: str,
):
    if not action_id:
        return None

    if not utils.security.Action_CanRead(db, user.id, action_id, -1):
        raise PermissionDeniedException()

    res = crud.action_comment.create(
        db,
        schemas.Action_Comment(
            action_id=action_id,
            user_id=user.id,
            comment=comment,
        ),
    )

    # --------------------------------------------
    # send email

    action = crud.action.get_kw_single(db, id=action_id)
    context = {
        "action": action,
        "comment": comment,
        "created_by": user.name,
    }
    header = "New Comment"
    subject = "New Comment on Action"
    email.action_comment_email(db, subject, header, context)

    # --------------------------------------------
    return res


@router.post("/send_email")
def send_action_email(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action_id: int,
):
    def format_datetime(date: datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")

    if not utils.security.Action_CanRead(db, user.id, action_id, -1):
        raise PermissionDeniedException()

    action = crud.action.get_kw_single(db, id=action_id)

    if action.type == "ACE":
        recipient_ids = action.member_ids if action.member_ids else []
        recipient_ids.append(action.owner_id)
        recipient_ids = list(set(recipient_ids))
        emails = db.query(schemas.User.email).filter(schemas.User.id.in_(recipient_ids)).all()
        emails = [x.email for x in emails]

        subject = (
            "New ACE Action Created"
            if format_datetime(action.created) == format_datetime(action.updated)
            else "Updated ACE Action"
        )
        header = (
            "New ACE Action"
            if format_datetime(action.created) == format_datetime(action.updated)
            else "Updated ACE Action"
        )
        email.action_email(db, emails, subject, header, action)


# ------------------
# READ
# ------------------
@router.get("", response_model=list[models.Action])
def get_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    if not utils.security.Action_CanRead(db, user.id, id, -1):
        raise PermissionDeniedException()
    return crud.action.get_kw(db, id=id)


@router.get("/for_group", response_model=list[models.Action])
def get_actions_for_group(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    workgroup_id: int = None,
):
    if not utils.security.Workgroup_CanRead(db, user.id, workgroup_id):
        raise PermissionDeniedException()

    workgroup = crud.workgroup.get(db, id=workgroup_id)
    return workgroup.actions


@router.get("/{id}", response_model=models.Action)
def get_single_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    if not utils.security.Action_CanRead(db, user.id, id, -1):
        raise PermissionDeniedException()
    return crud.action.get_kw_single(db, id=id)


@router.post("/get_page", response_model=models.PaginationResult[models.Action])
def get_action_page(
    *,
    db: Session = Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: list[crud.Rules] = Body(None),
    extra_filters: models.Actions_Filters,
):
    extra_filters = extra_filters.dict(exclude_unset=True)
    extra_filters["user"] = user

    # filter out archived actions by default if not specified
    if not any(x.field == "is_archived" for x in filters):
        extra_filters["is_archived"] = False

    return crud.action.get_items_by_rules(
        db, filters, extra_filters, user, page, count, sort_by, sort_desc
    )


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
    workgroup_id: int = None,
):
    edits = models.Action(**json.loads(action))

    creation = False

    # new actions are ACE actions
    if not edits.id:
        edits.type = "ACE"  # specify ACE type
        creation = True
    else:
        # Editing action, check permissions
        if not utils.security.Action_CanEdit(db, user.id, edits.id, workgroup_id):
            raise PermissionDeniedException()

    # --------------------------------------------
    # cherry pick new attachments only

    file_metadatas = []
    for x in edits.general_attachments:
        if not x.id:
            file_metadatas.append(x)

    # --------------------------------------------
    del[edits.privacy] # This is for the case where we are editing, and have added the action a group that changes it privacy,
                        # If you then clicked save on the action, without this line, it would revert the privacy change. Dont want that.
                        
    action = crud.action.update(db, edits)

    # --------------------------------------------
    # handle attachments

    if attachments:
        utils.upload_attachments(
            db, schemas.Action_Attachment, action.id, user, attachments, file_metadatas
        )

    # --------------------------------------------
    # append action to workgroup (if specified)
    #   used only when creating NEW actions directly from workgroups
    if workgroup_id:
        crud.workgroup_action_association.create(
            db,
            schemas.Workgroup_Action_Association(
                workgroup_id=workgroup_id,
                action_id=action.id,
            ),
        )

    # --------------------------------------------
    # create action log

    if creation:
        crud.log.create_action_log(db, LogTypeEnum.ACTION_CREATION, user.id, action.id)
    else:
        crud.log.create_action_log(db, LogTypeEnum.ACTION_UPDATE, user.id, action.id)

    # --------------------------------------------

    return action


@router.patch("/append_action_to_workgroup")
def append_action_to_workgroup(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    workgroup_id: int,
    action_id: int,
    workgroup_privacy: PrivacyEnum,
    action_privacy: PrivacyEnum,
    return_action_response: bool = False,
):
    if not utils.security.Workgroup_CanEdit(db, user.id, workgroup_id):
        raise PermissionDeniedException()

    crud.workgroup_action_association.append_action_to_workgroup(
        db, workgroup_id, action_id, workgroup_privacy, action_privacy
    )

    # RETURN
    if return_action_response:
        return models.Action.from_orm(crud.action.get(db, id=action_id))
    # return models.Workgroup_Title.from_orm(crud.workgroup.get(db, id=workgroup_id))

    # return list of workgroups models
    workgroup_ids = crud.workgroup_action_association.get_kw(db, action_id=action_id)
    workgroup_ids = [x.workgroup_id for x in workgroup_ids]
    return crud.workgroup.get_all(db, ids=workgroup_ids)


@router.patch("/update_archive_status")
def update_archive_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    action_id: int,
    is_archived: bool,
):
    if not utils.security.Action_CanEdit(db, user.id, action_id, -1):
        raise PermissionDeniedException()

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
