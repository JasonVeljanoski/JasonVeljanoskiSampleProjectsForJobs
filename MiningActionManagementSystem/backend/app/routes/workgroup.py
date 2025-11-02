import json
from datetime import datetime
from typing import Union

from app import crud, email, models, schemas, utils
from app.schemas.enums import LogTypeEnum, PrivacyEnum
from app.utils.errors import PermissionDeniedException
from fastapi import APIRouter, Body, Depends, File, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()

# ------------------
# CREATE
# ------------------
@router.post("", response_model=models.Workgroup_Full)
def create_workgroup(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: models.Workgroup,
):

    if edits.id:
        # Editing a workgroup, so check have permission to do so
        if not utils.security.Workgroup_CanEdit(db, user.id, edits.id):
            raise PermissionDeniedException()

    # --------------------------------------------
    # create or update workgroup
    workgroup = crud.workgroup.create(db, edits)

    # --------------------------------------------

    # --------------------------------------------
    # create workgroup log

    """
    crud.workgroup_log.create(
        db,
        schemas.Workgroup_Log(
            workgroup_id=workgroup.id,
            user_id=user.id,
        ),
    )
    """  # TODO - put proper log

    # --------------------------------------------

    return workgroup


@router.post("/comment")
def create_comment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    workgroup_id: int,
    comment: str,
):
    if not workgroup_id:
        return None

    if not utils.security.Workgroup_CanRead(db, user.id, workgroup_id):
        raise PermissionDeniedException()

    res = crud.workgroup_comment.create(
        db,
        schemas.Workgroup_Comment(
            workgroup_id=workgroup_id,
            user_id=user.id,
            comment=comment,
        ),
    )

    # --------------------------------------------
    # send email

    group = crud.workgroup.get_kw_single(db, id=workgroup_id)
    context = {
        "group": group,
        "comment": comment,
        "created_by": user.name,
    }
    header = "New Comment"
    subject = "New Comment on Group"
    email.group_comment_email(db, subject, header, context)

    # --------------------------------------------
    return res


@router.post("/send_email")
def send_workgroup_email(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    workgroup_id: int,
):
    def format_datetime(date: datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")

    if not utils.security.Workgroup_CanRead(db, user.id, workgroup_id):
        raise PermissionDeniedException()

    workgroup = crud.workgroup.get_kw_single(db, id=workgroup_id)

    recipient_ids = workgroup.member_ids if workgroup.member_ids else []
    recipient_ids += workgroup.admin_ids
    recipient_ids.append(workgroup.owner_id)
    recipient_ids = list(set(recipient_ids))
    emails = db.query(schemas.User.email).filter(schemas.User.id.in_(recipient_ids)).all()
    emails = [x.email for x in emails]

    subject = (
        "New ACE Workgroup Created"
        if format_datetime(workgroup.created) == format_datetime(workgroup.updated)
        else "Updated ACE Workgroup"
    )
    header = (
        "New ACE Workgroup"
        if format_datetime(workgroup.created) == format_datetime(workgroup.updated)
        else "Updated ACE Workgroup"
    )
    email.workgroup_email(db, emails, subject, header, workgroup)


# ------------------
# READ
# ------------------
@router.get("", response_model=models.Workgroup_Full)
def get_workgroup(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    if not utils.security.Workgroup_CanRead(db, user.id, id):
        raise PermissionDeniedException()
    return crud.workgroup.get(db, id=id)


@router.get("/of_action", response_model=list[models.Workgroup])
def get_workgroup_of_action(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    action_id: int,
):
    ids = crud.workgroup_action_association.get_kw(db, action_id=action_id)
    ids = [x.workgroup_id for x in ids]
    return crud.workgroup.get_all(db, ids=ids)


@router.post("/get_page", response_model=models.PaginationResult[models.Workgroup])
def get_page(
    *,
    db: Session = Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: list[crud.Rules] = Body(None),
    extra_filters: models.Workgroup_Filters,
):
    extra_filters = extra_filters.dict(exclude_unset=True)

    # filter out archived actions by default if not specified
    if not any(x.field == "is_archived" for x in filters):
        extra_filters["is_archived"] = False

    return crud.workgroup.get_items_by_rules(
        db, filters, extra_filters, user, page, count, sort_by, sort_desc
    )


# ------------------
# UPDATE
# ------------------
@router.put("", response_model=models.Workgroup_Full)
def create_update_workgroup(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    workgroup: str = Body(...),
    attachments: list[UploadFile] = File(...),
):
    edits = models.Workgroup_Full(**json.loads(workgroup))

    # Determine if newly created or editing - for log purposes
    creation = False
    if not edits.id:
        creation = True
    else:
        # Editing a workgroup, so check permissions
        if not utils.security.Workgroup_CanEdit(db, user.id, edits.id):
            raise PermissionDeniedException()

    # --------------------------------------------
    # create workgroup action associations manually due to unique permissions

    action_ids = edits.action_ids
    del edits.action_ids

    # --------------------------------------------
    # create or update workgroup

    workgroup = crud.workgroup.update(db, edits)

    # --------------------------------------------
    # handle attachments

    # cherry pick new attachments only
    file_metadatas = []
    for x in edits.general_attachments:
        if not x.id:
            file_metadatas.append(x)

    if attachments:
        utils.upload_attachments(
            db, schemas.Workgroup_Attachment, workgroup.id, user, attachments, file_metadatas
        )

    # Set the privacy of the workgroup + potentially any actions inside the workgroup
    crud.workgroup.update_privacy(db, user, edits.privacy, workgroup.id)
    db.refresh(workgroup)

    # --------------------------------------------
    # handle workgroup action association with permissions
    for id in action_ids:
        action = crud.action.get_kw_single(db, id=id)
        crud.workgroup_action_association.append_action_to_workgroup(
            db, workgroup.id, id, workgroup.privacy, action.privacy
        )

    # --------------------------------------------
    # create workgroup log

    if creation:
        crud.log.create_workgroup_log(db, LogTypeEnum.WORKGROUP_CREATION, user.id, workgroup.id)
    else:
        crud.log.create_workgroup_log(db, LogTypeEnum.WORKGROUP_UPDATE, user.id, workgroup.id)

    # --------------------------------------------

    return workgroup


@router.patch("/update_archive_status")
def update_archive_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    workgroup_id: int,
    is_archived: bool,
):
    if not utils.security.Workgroup_CanEdit(db, user.id, workgroup_id):
        raise PermissionDeniedException()

    if workgroup_id:
        db.query(schemas.Workgroup).filter(schemas.Workgroup.id == workgroup_id).update(
            {
                "is_archived": is_archived,
                "archive_user_id": user.id,
                "updated": utils.get_time_now(),
                "archive_datetime": utils.get_time_now(),
            }
        )
        db.commit()
