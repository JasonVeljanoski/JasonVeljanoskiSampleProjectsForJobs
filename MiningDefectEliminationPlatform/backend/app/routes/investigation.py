import json
import os
import subprocess

from fastapi import APIRouter, Body, Depends, File, UploadFile

from app import crud, email, models, schemas, utils
from app.schemas.enums import DocumentPaths

router = APIRouter()


# ------------------
# READ
# ------------------
@router.get("", response_model=models.Investigation_Full)
def get_full_investigation(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    return crud.investigation.get(db, id=id)


@router.get("/titles", response_model=list[models.Investigation_Title])
def get_investigation_titles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.investigation.all(db)


@router.post("/get_page", response_model=models.PaginationResult[models.Investigation_Light])
def get_investigation_page(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: models.Investigations_Filters = Body(None),
):
    filters = filters.dict(exclude_unset=True)
    filters["user_id"] = user.id

    return crud.investigation.get_page(db, page, count, sort_by, sort_desc, **filters)


@router.get("/user_open", response_model=list[models.Investigation_Full])
def get_user_investigations(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.investigation.get_user_open_investigations(db, user_id=user.id)


@router.get("/owner_ids", response_model=list[int])
def get_investigation_owner_ids(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    id: int,
):
    return crud.investigation.get_kw_single(db, id=id).owner_ids


# ------------------
# UPDATE
# ------------------
@router.put("/create_update", response_model=models.Investigation_Full)
def create_update_investigation(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation: str = Body(...),
    files: list[UploadFile] = File(...),
):
    edits = models.Investigation_With_Attachments(**json.loads(investigation))
    file_metadatas = edits.genertal_attachments_metas

    # GET OLD OWNERS/SUPERVISOR
    _old = crud.investigation.get(db, edits.id)
    old_owners = []
    if _old:
        old_owners = old_owners + _old.owner_ids
        old_owners.append(_old.supervisor_id)

    # DO CREATE/UPDATE
    edits.aplus_delay_events = [
        models.APLUS_Selected_Event_Details_Association(
            id=None, investigation_id=edits.id, event_id=x
        )
        for x in edits.aplus_delay_event_ids
    ]
    edits.rems_delay_events = [
        models.REMS_Selected_Event_Details_Association(
            id=None, investigation_id=edits.id, event_id=x
        )
        for x in edits.rems_delay_event_ids
    ]
    edits.owners = [
        models.Investigation_Owner_Association(id=None, investigation_id=edits.id, user_id=x)
        for x in edits.owner_ids
    ]

    new = crud.investigation.update(db, edits)

    # ------------------

    if files:
        utils.upload_attachments(
            db, schemas.Investigation_Attachment, new.id, user, files, file_metadatas
        )
    # ------------------

    db.commit()
    db.refresh(new)

    # ------------------

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            investigation_id=new.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.INVESTIGATION,
        ),
    )

    # ------------------

    # BROADCAST ALERTS
    if not edits.noEmail == True:
        utils.broadcast_investigation_alert(db, new.id, new.title, old_owners, edits.id == None)

    return new


@router.put("/save_relevant", response_model=list[models.Relevant_Investigation_Association])
def save_relevant(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    relevant_investigations: list[models.Relevant_Investigation_Association],
    investigation_id: int,
):
    crud.relevant_investigation_association.delete_kw(db, investigation_id=investigation_id)
    res = crud.relevant_investigation_association.update_all(db, relevant_investigations)

    # --------------------------------------

    db.query(schemas.Investigation).filter(schemas.Investigation.id == investigation_id).update(
        {"updated": utils.get_time_now()}
    )

    # --------------------------------------

    utils.create_notification(
        db,
        user.id,
        "Relevant Investigation Successfully Updated",
        "Relevant investigation list has updated",
    )

    return res


@router.put("/create_update/root_cause_detail", response_model=models.Root_Cause_Detail)
def create_root_cause_detail(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    root_cause_detail: models.Root_Cause_Detail,
):

    # ! POSSIBLY NOT NEEDED CODE ----
    rca_doc = utils.create_upload_files(
        [root_cause_detail.rca_doc],
        schemas.DocumentPaths.RCA.value,
        base_name=f"rca_complete_{root_cause_detail.investigation_id}",
        suffix="docx",
    )
    attachments = rca_doc

    # CREATE COMPLETED RCA DOC PDF FOR PREVIEW
    # remove existing pdf (if any)
    if rca_doc:
        filename = rca_doc[0].filename
        filename_noext = os.path.splitext(filename)[0]
        pdf_path = f"{DocumentPaths.RCA}/{filename_noext}.pdf"
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # create temp pdf
        command = f"libreoffice --headless --convert-to pdf --outdir app/attachments/rca app/attachments/rca/{filename}"
        subprocess.run(
            ["sh", "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    # ! ----------------------------

    # UPDATE
    if root_cause_detail.created == None:
        root_cause_detail.created = utils.get_time_now()

    res = crud.root_cause_detail.update(db, root_cause_detail, commit=False)
    res.attachments = attachments

    db.commit()
    db.refresh(res)

    # --------------------------------------

    for action in root_cause_detail.actions:
        db.query(schemas.Action).filter(schemas.Action.id == action.id).update(
            {"root_cause_detail_id": res.id, "updated": utils.get_time_now()}
        )

        # BRAND NEW ACTION
        # todo: refactor needed. Find if new action should be its own function
        # todo: this statement is used more than once and new actions types added would make it hard to maintain
        if (
            not action.flash_report_id
            and not action.five_why_id
            and not action.root_cause_detail_id
        ):
            utils.broadcast_action_alert(db, action.id, [], True)

    # --------------------------------------

    db.query(schemas.Investigation).filter(
        schemas.Investigation.id == root_cause_detail.investigation_id
    ).update({"updated": utils.get_time_now(), "cause_code": root_cause_detail.cause_code})

    # --------------------------------------

    utils.create_notification(db, user.id, "Root Cause Details", "Section was updated successfully")

    # --------------------------------------

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            root_cause_detail_id=res.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.ROOT_CAUSE,
        ),
    )

    # --------------------------------------

    return res


@router.put("/create_update/shared_learnings", response_model=models.Shared_Learning)
def create_update_shared_learnings(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    edits: models.Shared_Learning,
):
    shared_learning = crud.shared_learning.update(db, edits, commit=False)

    shared_learning.attachments = utils.create_upload_files(
        edits.initiative_images,
        schemas.ImgPath.SHARED_LEARNING.value,
        base_name="shared_learning",
        suffix="jpeg",
    )

    db.commit()
    db.refresh(shared_learning)

    # --------------------------------------

    db.query(schemas.Investigation).filter(
        schemas.Investigation.id == edits.investigation_id
    ).update({"updated": utils.get_time_now()})

    # --------------------------------------

    # BROADCAST ALERTS
    utils.create_notification(db, user.id, "Shared Learnings", "Section was updated successfully")

    # --------------------------------------

    # update logs to document who/when changed things
    crud.log.create(
        db,
        schemas.Log(
            shared_learning_id=shared_learning.id,
            user_id=user.id,
            log_type=schemas.enums.LogEnum.SHARED_LEARNINGS,
        ),
    )

    # --------------------------------------

    return shared_learning


# ---------------------------------------------------------------


@router.patch("/save_steps")
def save_steps(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation_id: int,
    steps_completed: int,
):
    current_steps_completed = (
        db.query(schemas.Investigation.steps_completed)
        .filter(schemas.Investigation.id == investigation_id)
        .scalar()
    )

    # if steps complete is greater than what is currently saved or if currently saved None (i.e. step 0)
    if not current_steps_completed or (
        steps_completed >= 0 and steps_completed > current_steps_completed
    ):
        db.query(schemas.Investigation).filter(schemas.Investigation.id == investigation_id).update(
            {"steps_completed": steps_completed, "updated": utils.get_time_now()}
        )
        db.commit()


@router.patch("/update_archive_status")
def update_archive_status(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    investigation_id: int,
    is_archived: bool,
):
    if investigation_id:
        db.query(schemas.Investigation).filter(schemas.Investigation.id == investigation_id).update(
            {
                "is_archived": is_archived,
                "archive_user_id": user.id,
                "updated": utils.get_time_now(),
                "archive_datetime": utils.get_time_now(),
            }
        )
        db.commit()

        # BROADCAST ALERTS
        utils.broadcast_investigation_update_socket(db, investigation_id)
