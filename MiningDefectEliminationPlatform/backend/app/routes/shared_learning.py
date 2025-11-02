import json
import os
import subprocess

from fastapi import APIRouter, Body, Depends, File, UploadFile

from app import crud, models, schemas, utils
from app.schemas.enums import DocumentPaths

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("/upload", response_model=models.General_Attachment)
def upload(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    attachment: UploadFile = File(...),
    metadata: str = Body(...),
    shared_learning_id: int,
):

    metadata = models.General_Attachment_Meta(**json.loads(metadata))

    res = None
    if attachment:
        res = utils.upload_attachments(
            db,
            schemas.Shared_Learning_Attachment,
            shared_learning_id,
            user,
            [attachment],
            [metadata],
        )

    return res[0] if res else None


# ------------------
# READ
# ------------------
@router.get("/attachments", response_model=list[models.General_Attachment])
def get_attachments(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    shared_learning_id: int,
):
    return crud.shared_learning_attachment.get_kw(
        db, type="Shared_Learning", shared_learning_id=shared_learning_id
    )


# ------------------
# UPDATE
# ------------------
@router.patch("/selected")
def update_selected(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    filename: str,
    shared_learning_id: int,
    flag: bool,
):
    """
    Note: Vulnerable to shell injection attack
    """

    # GLOBALS
    filename_noext = filename.split(".")[0] if "." in filename else None

    if not filename_noext:
        raise utils.errors.PDFGenerationFail

    # CONTEXT
    pdf_path = f"{DocumentPaths.SHARED_LEARNING.value}/{filename_noext}.pdf"
    command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.SHARED_LEARNING.value} {DocumentPaths.GENERAL.value}/{filename}"

    if not flag:
        db.query(schemas.Shared_Learning).filter(
            schemas.Shared_Learning.id == shared_learning_id
        ).update(
            {
                "use_custom_report": False,
                "updated": utils.get_time_now(),
                "custom_report_fname": None,
            }
        )
        db.commit()
        return None

    # do not do anything if file already exists
    if pdf_path and os.path.exists(pdf_path):
        # UPDATE DB
        db.query(schemas.Shared_Learning).filter(
            schemas.Shared_Learning.id == shared_learning_id
        ).update(
            {
                "use_custom_report": flag,
                "updated": utils.get_time_now(),
                "custom_report_fname": f"{filename_noext}.pdf",
            }
        )
        db.commit()
        return None

    # --------------------------------------

    # GENERATE NEW
    if command:
        result = subprocess.run(
            ["sh", "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            # Try Again ...
            result = subprocess.run(
                ["sh", "-c", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                raise utils.errors.PDFGenerationFail
    else:
        raise utils.errors.PDFGenerationFail

    # --------------------------------------

    # UPDATE DB
    db.query(schemas.Shared_Learning).filter(
        schemas.Shared_Learning.id == shared_learning_id
    ).update(
        {
            "use_custom_report": True,
            "updated": utils.get_time_now(),
            "custom_report_fname": f"{filename_noext}.pdf",
        }
    )
    db.commit()

    # --------------------------------------

    return {"success": True}
