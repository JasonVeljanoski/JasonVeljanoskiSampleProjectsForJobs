import os
import subprocess
from typing import Union

from fastapi import APIRouter, Body, Depends, UploadFile
from fastapi.responses import FileResponse

from app import crud, schemas, utils
from app.schemas.enums import DocumentPaths, TemplateDocNames

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("/generate_pdf", response_model=int)
def generate_pdf(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    filename: str,
    document_path: DocumentPaths,
):
    """
    Note: Vulnerable to shell injection attack
    """
    # Handle shell injection attack
    # todo: similar to the below
    # if not os.path.exists(document_path):
    #     raise utils.errors.PDFGenerationFail

    # GLOBALS
    filename_noext = filename.split(".")[0] if "." in filename else None
    file_ext = filename.split(".")[-1] if "." in filename else None
    command = None
    pdf_path = None

    if not filename_noext:
        raise utils.errors.PDFGenerationFail

    # CONTEXT
    # --writer-pdf-export 'ExportImagesCompressionMode=1 ExportImagesDPI=300'
    if document_path == DocumentPaths.FIVE_WHY:
        pdf_path = f"{DocumentPaths.FIVE_WHY.value}/{filename_noext}.pdf"
        command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.FIVE_WHY.value} {DocumentPaths.FIVE_WHY.value}/{filename}"
    elif document_path == DocumentPaths.FLASH_REPORT:
        pdf_path = f"{DocumentPaths.FLASH_REPORT.value}/{filename_noext}.pdf"
        command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.FLASH_REPORT.value} {DocumentPaths.FLASH_REPORT.value}/{filename}"
    elif document_path == DocumentPaths.RCA:
        if file_ext == "pdf":
            return
        pdf_path = f"{DocumentPaths.RCA.value}/{filename_noext}.pdf"
        command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.RCA.value} {DocumentPaths.RCA.value}/{filename}"
    elif document_path == DocumentPaths.SHARED_LEARNING:
        pdf_path = f"{DocumentPaths.SHARED_LEARNING.value}/{filename_noext}.pdf"
        command = f"libreoffice --headless --convert-to pdf --outdir {DocumentPaths.SHARED_LEARNING.value} {DocumentPaths.SHARED_LEARNING.value}/{filename}"

    # REMOVE EXISTING
    if pdf_path and os.path.exists(pdf_path):
        os.remove(pdf_path)

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


# -----------------------------------------------------


@router.post("/create_flash_report")
def create_flashreport_document(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation_id: int,
):
    def get_status(value):
        if value == schemas.enums.StatusEnum.OPEN:
            return "Open"
        elif value == schemas.enums.StatusEnum.ON_HOLD:
            return "On Hold"
        elif value == schemas.enums.StatusEnum.CLOSED:
            return "Closed"
        return "Open"

    # get data
    investigation = crud.investigation.get(db, investigation_id)
    flash_report = investigation.flash_report

    # meta
    filename = f"flash_report_{investigation_id}.pptx"
    total_effective_duration = investigation.total_effective_duration
    total_event_duration = investigation.total_event_duration
    total_lost_tonnes = investigation.total_tonnes_lost

    # construct actions object
    actions = []
    for action in flash_report.actions:
        if not action.is_archived:
            actions.append(
                {
                    "title": action.title,
                    "description": action.description,
                    "status": get_status(action.status),
                    "date_closed": utils.format_date(action.date_closed),
                    "priority": action.priority.value,
                    "owners": action.owner_users,
                    "date_due": utils.format_date(action.date_due),
                }
            )

    context = {
        "function_location": investigation.function_location,
        "equipment": investigation.equipment_description,
        "object_type": investigation.object_type,
        "object_part": investigation.object_part_description,
        "damage_code": investigation.damage_code,
        # ------------------------
        "event_type": investigation.event_type,
        "site": investigation.site,
        "department": investigation.department,
        "title": flash_report.event_title,
        "owners": investigation.owner_users,
        "event_date": utils.format_date(investigation.event_datetime),
        "event_time": utils.format_time(investigation.event_datetime),
        "event_description": flash_report.event_description,
        "event_duration": total_event_duration,
        "effective_duration": total_effective_duration,
        "lost_tonnes": total_lost_tonnes,
        "business_impact": flash_report.business_impact,
        "immediate_action": flash_report.immediate_action_taken,
        "root_causes": [root_cause for root_cause in flash_report.potential_root_causes],
        "actions": actions,
        "filenames": [file for file in flash_report.filenames],
        "sufficient_inventory_levels": flash_report.sufficient_inventory_levels,
    }

    utils.flashreport_pptx_template(context, filename)


# -----------------------------------------------------


@router.post("/create_five_why")
def create_fivewhy_document(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation_id: int,
):
    # build context
    investigation = crud.investigation.get(db, investigation_id)

    context = utils.build_fivewhy_context(investigation)

    # render document
    FILE_NAME = f"five_why_{investigation.id}.docx"
    TEMPLATE_PATH = f"{DocumentPaths.TEMPLATES.value}/{TemplateDocNames.FIVE_WHY.value}"
    OFFICE_PATH = f"{DocumentPaths.FIVE_WHY.value}/{FILE_NAME}"

    utils.render_save_five_why_template(context, TEMPLATE_PATH, OFFICE_PATH)


# -----------------------------------------------------


@router.post("/create_rca")
def create_rca_document(
    *,
    user: schemas.User = utils.IS_WRITER,
    filename: str,
    site: str = None,
    department: str = None,
):
    TEMPLATE_PATH = f"{DocumentPaths.TEMPLATES.value}/{TemplateDocNames.RCA.value}"
    OFFICE_PATH = f"{DocumentPaths.RCA.value}/{filename}"

    context = {"site": site, "department": department}

    utils.render_docxtemplate(context, TEMPLATE_PATH, OFFICE_PATH)


@router.post("/upload_complete_rca")
def upload_complete_rca(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    file: UploadFile,
    old_filename: str = Body(...),
    root_cause_detail_id: int = Body(...),
    investigation_id: int = Body(...),
):
    ext = file.filename.split(".")[-1]
    if ext != "docx" and ext != "pdf":
        return

    # REMOVE EXISTING (pdf or docx)
    OLD_RCA_PATH = f"{DocumentPaths.RCA.value}/{old_filename}"
    if OLD_RCA_PATH and os.path.exists(OLD_RCA_PATH):
        print("\n\n\n ====> removing old file \n\n\n")
        os.remove(OLD_RCA_PATH)

    fname = utils.get_unique_randomizer(ext)
    try:
        RCA_PATH = f"{DocumentPaths.RCA.value}/{fname}"
        with open(RCA_PATH, "wb") as f:
            f.write(file.file.read())

        # update investigations has_completed_rca flag
        investigation = crud.investigation.get(db, investigation_id)
        investigation.has_completed_rca = True
    except:
        raise utils.errors.FileUpload
    finally:
        # --------------------------------------

        db.query(schemas.Root_Cause_Detail).filter(
            schemas.Root_Cause_Detail.id == root_cause_detail_id
        ).update({"updated": utils.get_time_now(), "complete_rca_fname": fname})

        db.commit()

        # --------------------------------------

    return fname


# -----------------------------------------------------


@router.post("/create_shared_learnings")
def create_shared_learnings_document(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation_id: int,
):
    def get_status(value):
        if value == schemas.enums.StatusEnum.OPEN:
            return "Open"
        elif value == schemas.enums.StatusEnum.ON_HOLD:
            return "On Hold"
        elif value == schemas.enums.StatusEnum.CLOSED:
            return "Closed"
        return "Open"

    # get data
    investigation = crud.investigation.get(db, investigation_id)
    shared_learning_actions = crud.action.get_shared_learning_actions(
        db, investigation_id=investigation_id
    )

    shared_learning = investigation.shared_learning

    if not shared_learning:
        return

    # meta
    filename = f"shared_learnings_{investigation_id}.pptx"

    # ------------------------------------------------------

    # construct actions object
    actions = []
    for action in shared_learning_actions:
        actions.append(
            {
                "title": action.title,
                "description": action.description,
                "status": get_status(action.status),
                "priority": action.priority.value,
                "owners": action.owner_users,
                "date_due": utils.format_date(action.date_due),
                "date_closed": utils.format_date(action.date_closed),
            }
        )

    # ------------------------------------------------------

    context = {
        "site": investigation.site,
        "department": investigation.department,
        "function_location": investigation.function_location,
        "equipment": investigation.equipment_description,
        "object_type": investigation.object_type,
        "object_part": investigation.object_part_description,
        "damage_code": investigation.damage_code,
        "cause_code": investigation.root_cause_detail.cause_code
        if investigation.root_cause_detail
        else None,
        "event_date": utils.format_date(investigation.event_datetime),
        "event_time": utils.format_time(investigation.event_datetime),
        # --------------
        "title": shared_learning.event_title,
        "event_description": shared_learning.event_description,
        "owners": investigation.owner_users,
        # --------------
        "cause_category": investigation.root_cause_detail.cause_category
        if investigation.root_cause_detail
        else None,
        # --------------
        "reason": shared_learning.reason,
        "shared_learnings": shared_learning.shared_learning,
        # --------------
        "flashreport_filename": investigation.flash_report.filenames[0],
        "initiative_image_filename": shared_learning.initiative_image_filenames[0]
        if len(shared_learning.initiative_images) > 0
        else None,
        # --------------
        "actions": actions,
    }

    utils.shared_learning_pptx_template(context, filename)


# ------------------
# READ
# ------------------
@router.get("/exists/{file_path:path}")
def does_doc_exist(
    *,
    user: schemas.User = utils.IS_LOGGED_IN,
    file_path: str,
):
    return file_path and os.path.exists(file_path)


@router.post("/remove/{file_path:path}")
def remove_attachment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    attachment_id: int,
    file_path: str,
):
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
    user: schemas.User = utils.IS_LOGGED_IN,
    file_path: str,
    render_key: Union[int, None] = None,
):
    if file_path and os.path.exists(file_path):
        return FileResponse(file_path)
    raise utils.errors.FileNotFound
