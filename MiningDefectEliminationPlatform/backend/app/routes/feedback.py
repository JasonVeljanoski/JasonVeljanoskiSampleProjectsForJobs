import json

from app import crud, email, models, schemas, utils
from fastapi import APIRouter, Body, Depends, File, UploadFile

router = APIRouter()


# ------------------
# READ
# ------------------
@router.get("", response_model=list[models.Feedback])
def get_feedback(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    return crud.feedback.get_kw(db, id=id)


@router.post("/get_page", response_model=models.PaginationResult[models.Feedback])
def get_feedback_page(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: models.Feedback_Filters = Body(None),
):
    filters = filters.dict(exclude_unset=True)

    # if admin, show all rows, otherwise show only users
    if user.access != schemas.user.Access.ADMIN:
        filters["user_id"] = user.id

    return crud.feedback.get_page(db, page, count, sort_by, sort_desc, **filters)


# ------------------
# UPDATE
# ------------------
@router.put("", response_model=models.Feedback)
def update_feedback(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: str = Body(...),
    attachments: list[UploadFile] = File(...),
):
    edits = models.Feedback_With_Attachments(**json.loads(edits))
    file_metadatas = edits.general_attachments_metas

    # ------------------

    edits.updated_by_id = user.id

    if not edits.id:
        edits.created_by_id = user.id

    # ------------------

    feedback = crud.feedback.update(db, edits, commit=True)

    # ------------------

    if attachments:
        utils.upload_attachments(
            db, schemas.Feedback_Attachment, feedback.id, user, attachments, file_metadatas
        )

    # ------------------

    # EMAIL
    # * Send email to all admins
    if edits.noEmail == True:
        admins = crud.user.get_kw(db, access=schemas.Access.ADMIN)
        for admin in admins:
            subject = f"Created Feedback Item #{feedback.id}"
            header = "A new feedback item is waiting for you"
            email.feedback_email(db, admin.email, subject, header, feedback)

    # ------------------

    db.commit()
    db.refresh(feedback)

    # ------------------

    return feedback


@router.patch("/add_comment", response_model=models.Feedback_Comment)
def add_comment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    feedback_id: int,
    comment: str,
):

    res = crud.feedback_comment.create(
        db,
        schemas.Feedback_Comment(
            feedback_id=feedback_id,
            user_id=user.id,
            comment=comment,
        ),
    )

    # general notification to this user
    utils.create_notification(
        db,
        user.id,
        "Comment Added",
        f"New comment added for feedback #{feedback_id}",
        tags=[],
        status="success",
    )

    return res
