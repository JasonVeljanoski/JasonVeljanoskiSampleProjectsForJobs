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
    flash_report_id: int,
):

    metadata = models.General_Attachment_Meta(**json.loads(metadata))

    res = None
    if attachment:
        res = utils.upload_attachments(
            db, schemas.Flash_Report_Attachment, flash_report_id, user, [attachment], [metadata]
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
    flash_report_id: int,
):
    return crud.flash_report_attachment.get_kw(
        db, type="Flash_Report", flash_report_id=flash_report_id
    )


# ------------------
# UPDATE
# ------------------
@router.put("/create_update", response_model=models.Flash_Report)
def create_update_flash_report(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: models.Flash_Report,
):
    flash_report = crud.flash_report.update(db, edits, commit=False)
    # flash_report.actions = utils.create_actions(flash_report_edits.actions)
    # flash_report.actions = flash_report_edits.actions

    flash_report.attachments = utils.create_upload_files(
        edits.files,
        schemas.ImgPath.FLASH_REPORT.value,
        base_name="flash_report",
        suffix="jpeg",
    )

    # --------------------------------------

    db.commit()
    db.refresh(flash_report)

    # --------------------------------------

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            flash_report_id=flash_report.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.FLASH_REPORT,
        ),
    )

    # --------------------------------------

    for action in edits.actions:
        db.query(schemas.Action).filter(schemas.Action.id == action.id).update(
            {"flash_report_id": flash_report.id, "updated": utils.get_time_now()}
        )

        # BRAND NEW ACTION
        if (
            not action.flash_report_id
            and not action.five_why_id
            and not action.root_cause_detail_id
        ):
            utils.broadcast_action_alert(db, action.id, [], True)

    # --------------------------------------

    db.query(schemas.Investigation).filter(
        schemas.Investigation.id == edits.investigation_id
    ).update({"updated": utils.get_time_now()})

    # --------------------------------------

    # BROADCAST ALERTS
    utils.create_notification(db, user.id, "Flash Report", "Section was updated successfully")

    # --------------------------------------

    return flash_report


@router.patch("/selected")
def update_selected(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    filename: str,
    flash_report_id: int,
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
    pdf_path = f"{DocumentPaths.FLASH_REPORT.value}/{filename_noext}.pdf"
    command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.FLASH_REPORT.value} {DocumentPaths.GENERAL.value}/{filename}"

    if not flag:
        db.query(schemas.Flash_Report).filter(schemas.Flash_Report.id == flash_report_id).update(
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
        db.query(schemas.Flash_Report).filter(schemas.Flash_Report.id == flash_report_id).update(
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
    db.query(schemas.Flash_Report).filter(schemas.Flash_Report.id == flash_report_id).update(
        {
            "use_custom_report": True,
            "updated": utils.get_time_now(),
            "custom_report_fname": f"{filename_noext}.pdf",
        }
    )
    db.commit()

    # --------------------------------------

    return {"success": True}
