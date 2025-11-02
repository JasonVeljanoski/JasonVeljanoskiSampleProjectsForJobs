from urllib.parse import urlencode

from fastapi import APIRouter, Body, Depends

from app import utils, email, schemas, crud, models
from app.crud import attachment

from sqlalchemy import or_, and_

router = APIRouter()


@router.post("")
def test(
    *,
    db=Depends(utils.get_db),
    site: str = Body(...),
    department: str = Body(...),
    object_type: str = Body(...),
    flash_report_id: int = Body(...),
    path: str = Body(...),
    message: str = Body(None),
    extra_users: list[str] = Body(None)
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

    users = [user.email for user in users]

    if extra_users:
        users = users + extra_users

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

    # ------------------------

    attachments = []
    attachments.append(path)

    # ------------------------

    email.flash_report_distribution(users, message, attachments, email_dic)
