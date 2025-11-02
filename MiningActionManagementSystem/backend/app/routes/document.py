import os
from typing import Union

from app import crud, schemas, utils
from app.utils.errors import PermissionDeniedException
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

router = APIRouter()


# ------------------
# routes are below this point for a reason (order matters)
# ------------------


@router.post("/remove/{file_path:path}")
def remove_attachment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    attachment_id: int,
    file_path: str,
):
    # Check permissions if it is Action type
    attachment = crud.general_attachment.get(db, attachment_id)
    if attachment.type == "Action":
        action_id = attachment.action_id
        if not utils.security.Action_CanEdit(db, user.id, action_id, -1):
            raise PermissionDeniedException()

    # change fields in database
    db.query(schemas.General_Attachment).filter(
        schemas.General_Attachment.id == attachment_id
    ).update(
        {
            "deleted": True,
            "deleted_date": utils.get_time_now(),
            "updated": utils.get_time_now(),
            "deleted_by": user.id,
        }
    )
    db.commit()

    # delete file
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise utils.errors.FileNotFound


@router.get("/{file_path:path}", response_class=FileResponse)
async def get_document(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    file_path: str,
    render_key: Union[int, None] = None,
):
    # To check permissions, first get the action that this file is attached to
    uniqueFilename = file_path.split("attachments/general/")[1]
    file_action_query = (
        db.query(schemas.Action_Attachment.action_id)
        .where(schemas.Action_Attachment.unique_filename == uniqueFilename)
        .distinct()
    )
    action_id_result = db.scalars(file_action_query).all()
    if len(action_id_result) > 0:
        action_id = action_id_result[0]
        if not utils.security.Action_CanRead(db, user.id, action_id, -1):
            raise PermissionDeniedException()

    if file_path and os.path.exists(file_path):
        return FileResponse(file_path)
    raise utils.errors.FileNotFound
