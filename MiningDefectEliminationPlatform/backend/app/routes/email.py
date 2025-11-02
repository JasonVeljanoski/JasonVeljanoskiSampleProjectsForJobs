from fastapi import APIRouter, Body, Depends
from sqlalchemy import and_, or_

from app import crud, email, models, schemas, utils

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("/broadcast_flash_report")
def broadcast_flash_report(
    *,
    db=Depends(utils.get_db),
    site: str = Body(...),
    department: str = Body(...),
    object_type: str = Body(...),
    flash_report_id: int = Body(...),
    path: str = Body(...),
    message: str = Body(None),
    extra_emails: list[str] = Body(None),
    download_name: str = Body(None),
):
    users = get_watched_groups(
        db=db,
        site=site,
        department=department,
        object_type=object_type,
    )

    if extra_emails:
        users = users + extra_emails

    # ------------------------------------------------

    flash_report = crud.flash_report.get(db, flash_report_id)
    if flash_report:
        flash_report = models.Flash_Report.from_orm(flash_report)
    else:
        raise utils.errors.CustomException(message="Flash Report does not exist!")

    # ------------------------

    investigation = crud.investigation.get(db, flash_report.investigation_id)
    # if investigation:
    #     investigation = models.Investigation_Light.from_orm(investigation)
    # else:
    #     raise utils.errors.CustomException(message="Flash Report error!")

    # ------------------------

    email_dic = {
        # flash report info
        "title": flash_report.event_title,
        "description": flash_report.event_description,
        "business_impact": flash_report.business_impact,
        "immediate_action_taken": flash_report.immediate_action_taken,
        "root_causes": flash_report.potential_root_causes,
        "image": None,
        "image_path": None,
        # investigation info
        "investigation_id": investigation.id,
        "event_date": utils.format_date(investigation.event_datetime),
        "site": investigation.site,
        "department": investigation.department,
        "function_location": investigation.function_location,
        "equipment_description": investigation.equipment_description,
        "object_type": investigation.object_type,
        "object_part_description": investigation.object_part_description,
        "damage_code": investigation.damage_code,
        "event_type": investigation.event_type,
        "total_event_duration": investigation.total_event_duration,
        "total_tonnes_lost": investigation.total_tonnes_lost,
        "total_effective_duration": investigation.total_effective_duration,
    }

    if len(flash_report.files):
        email_dic["image"] = flash_report.files[0]

    if len(flash_report.filenames):
        email_dic[
            "image_path"
        ] = f"{schemas.ImgPath.FLASH_REPORT.value}/{flash_report.filenames[0]}"

    # ------------------------

    attachments = []
    attachments.append(path)

    # ------------------------

    email.flash_report_distribution(
        users, message, email_dic, attachments, custom_attachment_names=[download_name]
    )


@router.post("/broadcast_shared_learnings")
def broadcast_shared_learnings(
    *,
    db=Depends(utils.get_db),
    site: str = Body(...),
    department: str = Body(...),
    object_type: str = Body(...),
    shared_learnings_id: int = Body(...),
    path: str = Body(...),
    message: str = Body(None),
    extra_emails: list[str] = Body(None),
    download_name: str = Body(None),
):
    def get_status(value):
        if value == schemas.enums.StatusEnum.OPEN:
            return "Open"
        elif value == schemas.enums.StatusEnum.ON_HOLD:
            return "On Hold"
        elif value == schemas.enums.StatusEnum.CLOSED:
            return "Closed"
        return "Open"

    users = get_watched_groups(
        db=db,
        site=site,
        department=department,
        object_type=object_type,
    )

    if extra_emails:
        users = users + extra_emails

    # ------------------------------------------------

    shared_learning = crud.shared_learning.get(db, shared_learnings_id)
    if shared_learning:
        shared_learning = models.Shared_Learning.from_orm(shared_learning)
    else:
        raise utils.errors.CustomException(message="Shared Learning document does not exist!")

    # ------------------------

    investigation = crud.investigation.get(db, shared_learning.investigation_id)
    # if investigation:
    #     investigation = models.Investigation_Light.from_orm(investigation)
    # else:
    #     raise utils.errors.CustomException(message="Flash Report error!")

    # ------------------------

    shared_learning_actions = crud.action.get_shared_learning_actions(
        db, investigation_id=investigation.id
    )

    # construct actions object
    actions = []
    for action in shared_learning_actions:
        actions.append(
            {
                "id": action.id,
                "title": action.title,
                "description": action.description,
                "status": get_status(action.status),
                "priority": action.priority.value,
                "owner_ids": [owner.id for owner in action.owners],
                "date_due": utils.format_date(action.date_due),
                "date_closed": utils.format_date(action.date_closed),
            }
        )

    # ------------------------

    email_dic = {
        # flash report info
        "title": shared_learning.event_title,
        "description": shared_learning.event_description,
        "reason": shared_learning.reason,
        "shared_learning": shared_learning.shared_learning,
        "image": None,
        "image_path": None,
        "cause_category_image": None,
        # investigation info
        "investigation_id": investigation.id,
        "event_date": utils.format_date(investigation.event_datetime),
        "site": investigation.site,
        "department": investigation.department,
        "function_location": investigation.function_location,
        "equipment_description": investigation.equipment_description,
        "object_type": investigation.object_type,
        "object_part_description": investigation.object_part_description,
        "damage_code": investigation.damage_code,
        "cause_code": investigation.root_cause_detail.cause_code,
        "cause_category": investigation.root_cause_detail.cause_category
        if investigation.root_cause_detail
        else None,
        # --------------
        "actions": actions,
    }

    if len(shared_learning.initiative_images):
        email_dic["image"] = shared_learning.initiative_images[0]

    if len(shared_learning.initiative_image_filenames):
        email_dic[
            "image_path"
        ] = f"{schemas.ImgPath.SHARED_LEARNING.value}/{shared_learning.initiative_image_filenames[0]}"

    # ------------------------

    attachments = []
    attachments.append(path)

    # ------------------------

    email.shared_learning_distribution(
        db, users, message, email_dic, attachments, custom_attachment_names=[download_name]
    )


@router.get("/get_watched_groups")
def get_watched_groups(
    *,
    db=Depends(utils.get_db),
    site: str,
    department: str,
    object_type: str,
):
    query = db.query(schemas.User)

    query = query.filter(schemas.User.is_user.is_(True))

    show_all_filter = schemas.User.watched_groups["show_all"].astext == "true"

    has_filters_set = []
    extra_filters = []

    def add_extra_field(field, value):
        has_filters_set.append(
            schemas.User.watched_groups[field].astext.isnot(None),
        )

        if value:
            extra_filters.append(
                or_(
                    schemas.User.watched_groups[field].astext.is_(None),
                    schemas.User.watched_groups[field].op("?")(value),
                )
            )

    add_extra_field("sites", site)
    add_extra_field("departments", department)
    add_extra_field("object_types", object_type)

    query = query.filter(
        or_(
            show_all_filter,
            and_(or_(*has_filters_set), *extra_filters),
        )
    )

    users = query.all()

    return [user.email for user in users]
