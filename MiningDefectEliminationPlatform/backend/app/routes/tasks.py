import csv
import datetime as dt
import json
import logging
import os
from typing import List

import pytz
from app import config, crud, email, schemas, utils
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import parse_obj_as
from sqlalchemy import (TIMESTAMP, Boolean, Column, Float, Integer, String,
                        and_, create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

utc = pytz.UTC
logger = logging.getLogger(__name__)

router = APIRouter()

BaseSF = declarative_base()

# ------------------
# CREATE
# ------------------

# TIMER TASKS
@router.post("/clean_attachments")
def clean_attachments(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    attachments = crud.attachment.all(db)
    fnames = [x.filename for x in attachments]
    count = 0

    # traverse root directory, and list directories as dirs and files as files
    for root, _, files in os.walk("app/attachments"):
        for file in files:
            if file not in fnames:
                os.remove(os.path.join(root, file))
                count += 1

    return f"{count} files have been deleted."


# ! THIS DROPPED PROD DATA ONCE UPON A TIME, BE CAREFUL
@router.post("/clean_actions")
def clean_actions(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    db.query(schemas.Action).filter(
        and_(
            schemas.Action.five_why_id == None,
            schemas.Action.flash_report_id == None,
            schemas.Action.root_cause_detail_id == None,
            schemas.Action.is_historical == 0,
        )
    ).update(
        {
            "is_deleted": True,
            "delete_user_id": None,
            "delete_datetime": utc.localize(dt.datetime.now()),
        }
    )

    db.commit()


@router.post("/snowflake_heartbeat")
def snowflake_heartbeat(
    *,
    db_sf=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
):
    """
    Snowflakes authentication token will expire after 4hours of being idle.
    Users will not be able to make requests to snowflake if this token is invalid.
    The aim here is to keep the token 'alive' by making a random request on a CRON job every 3Hours and 55Mins.
    """
    query = """
        select current_date(), current_time(), current_timestamp();
    """
    db_sf.execute(query).mappings().all()


@router.post("/flag_overdue_investigations")
def flag_overdue_investigations(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    open_investigations = crud.investigation.get_kw(db, status=schemas.StatusEnum.OPEN)
    time = utc.localize(dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    counter = 0

    for investigation in open_investigations:
        if investigation.completion_due_date and investigation.completion_due_date < time:
            investigation.status = schemas.StatusEnum.OVERDUE
            db.add(investigation)
            db.commit()

            counter += 1

    return f"{counter} investigations have been flagged as overdue."


# ------------------------------------------------------------------------------------------------


@router.post("/flag_overdue_actions")
def flag_overdue_actions(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    open_actions = crud.action.get_kw(db, status=schemas.StatusEnum.OPEN)
    time = utc.localize(dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    counter = 0

    for action in open_actions:
        if action.date_due and action.date_due < time:
            action.status = schemas.StatusEnum.OVERDUE
            db.add(action)
            db.commit()
            counter += 1

    return f"{counter} actions flagged as overdue."


# ----------------------------------------------------


@router.post("/warning_due_action")
def warning_due_action(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    def today_plus_days(days):
        return utc.localize(
            dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ) + dt.timedelta(days=days)

    open_actions = crud.action.get_kw(db, status=schemas.StatusEnum.OPEN)

    for action in open_actions:
        if action.date_due:
            action.date_due = utc.localize(dt.datetime.combine(action.date_due, dt.time.min))
            if action.date_due == today_plus_days(3):
                subject = "Action is due in 3 days"
                header = "Action is due in 3 days"
                users = [x.email for x in action.owner_users if x.email]
                email.action_email(db, users, subject, header, action)

            elif action.date_due == today_plus_days(7):
                subject = "Action is due in 7 days"
                header = "Action is due in 7 days"
                users = [x.email for x in action.owner_users if x.email]
                email.action_email(db, users, subject, header, action)


@router.post("/warning_due_investigation")
def warning_due_investigation(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    def today_plus_days(days):
        """Returns a datetime object of today + n days with the time set to 00:00:00"""

        return utc.localize(
            dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ) + dt.timedelta(days=days)

    open_investigations = crud.investigation.get_kw(db, status=schemas.StatusEnum.OPEN)

    for investigation in open_investigations:
        if investigation.completion_due_date:
            investigation.completion_due_date = utc.localize(
                dt.datetime.combine(investigation.completion_due_date, dt.time.min)
            )
            if investigation.completion_due_date == today_plus_days(3):
                subject = f"Investigation #{investigation.id} is due in 3 days"
                header = f"Investigation #{investigation.id} is due in 3 days"
                users = [x.email for x in investigation.owner_users if x.email]
                email.investigation_email(db, users, subject, header, investigation)

            elif investigation.completion_due_date == today_plus_days(7):
                subject = f"Investigation #{investigation.id} is due in 7 days"
                header = f"Investigation #{investigation.id} is due in 7 days"
                users = [x.email for x in investigation.owner_users if x.email]
                email.investigation_email(db, users, subject, header, investigation)


@router.post("/warning_due_all")
def warning_due_all(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    warning_due_action(db=db, valid=valid)
    warning_due_investigation(db=db, valid=valid)


# ----------------------------------------------------


# ----------------------------------------------------


@router.post("/all_tasks")
def all_tasks(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    clean_attachments(db=db, valid=valid)
    clean_actions(db=db, valid=valid)


@router.post("/all_flag_overdue_tasks")
def all_flag_overdue_tasks(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    inv_res = flag_overdue_investigations(db=db, valid=valid)
    act_res = flag_overdue_actions(db=db, valid=valid)

    print(inv_res)
    print(act_res)


# ----------------------------------------------------


def update_supervisores():
    db = next(utils.get_db())
    db_sf = next(utils.get_sf_db())

    sql = """
        SELECT  
            "SupervisorEmail", "EmployeeEmail", "SuperTier"
        FROM 
            AA_ASSETS_FIXEDPLANT.SELFSERVICE."ap_SupervisorTeams"
        WHERE 
            "SupervisorEmail" is not NULL and "EmployeeEmail" is not NULL and "SupervisorEmail" != "EmployeeEmail"
    """

    items = db_sf.execute(sql).fetchall()
    sorted_items = sorted(items, key=lambda x: x.SuperTier, reverse=True)

    logger.info(f"Found {len(items)} items")

    try:
        for item in items:

            employee = crud.user.get_kw_single(db, email=item.EmployeeEmail.lower())

            # update supervisor
            if employee:
                # filter items by employee email
                filtered_items = [
                    i for i in sorted_items if i.EmployeeEmail == item.EmployeeEmail.lower()
                ]
                # get supervisor email
                supervisor_email = (
                    filtered_items[0].SupervisorEmail if len(filtered_items) else None
                )
                immediate_supervisor = None
                if supervisor_email:
                    immediate_supervisor = crud.user.get_kw_single(
                        db, email=supervisor_email.lower()
                    )

                if immediate_supervisor:
                    employee.supervisor_id = immediate_supervisor.id
                    db.commit()
    except Exception as e:
        logger.exception(e)

    db.close()
    db_sf.close()


@router.post("/update_supervisors")
async def update_supervisores_task(
    background_tasks: BackgroundTasks,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
):
    background_tasks.add_task(update_supervisores)
    return {"message": "Updating supervisors in the background"}


# ------------------------------------------------------------------------------------------------
# CHARTING TASKS BELOW THIS LINE
# ------------------------------------------------------------------------------------------------


# For Snowflake export, custom classes
class LogSF(BaseSF):
    __tablename__ = "LOG"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    user_id = Column(Integer)
    log_type = Column(String)
    investigation_id = Column(Integer)
    flash_report_id = Column(Integer)
    five_why_id = Column(Integer)
    root_cause_detail_id = Column(Integer)
    shared_learning_id = Column(Integer)
    action_id = Column(Integer)


class InvestigationSF(BaseSF):
    __tablename__ = "INVESTIGATION"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    investigation_type = Column(String)
    event_datetime = Column(TIMESTAMP)
    completion_due_date = Column(TIMESTAMP)
    steps_completed = Column(Integer)
    function_location = Column(String)
    equipment_description = Column(String)
    object_type = Column(String)
    catalog_profile = Column(String)
    catalog_profiles = Column(String)  # Is array in database, convert to string
    object_part_description = Column(String)
    damage_code = Column(String)
    supervisor_email = Column(String)  # In database, is supervisor_id, convert to associated email
    event_type = Column(String)  # Enum
    status = Column(String)
    total_effective_duration = Column(Float)
    total_tonnes_lost = Column(Float)
    date_closed = Column(TIMESTAMP)
    total_event_duration = Column(Float)
    cause_code = Column(String)
    is_archived = Column(Boolean)
    archive_user_email = Column(String)  # archive_user_id
    archive_datetime = Column(TIMESTAMP)
    site = Column(String)
    department = Column(String)
    users = Column(String)
    aplus_delay_event_ids = Column(String)
    rems_delay_event_ids = Column(String)


class EquipmentSF(BaseSF):
    __tablename__ = "EQUIPMENT"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    function_location = Column(String)
    catalog_profile = Column(String)
    equipment_description = Column(String)
    object_type = Column(String)
    site = Column(String)
    department = Column(String)


class Flash_ReportSF(BaseSF):
    __tablename__ = "FLASH_REPORT"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    investigation_id = Column(Integer)
    event_title = Column(String)
    business_impact = Column(String)
    immediate_action_taken = Column(String)
    potential_root_causes = Column(String)  # In database, is array, convert to string
    event_description = Column(String)


class Root_Cause_DetailSF(BaseSF):
    __tablename__ = "ROOT_CAUSE_DETAIL"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    investigation_id = Column(Integer)
    description = Column(String)
    additional_contribution_factors = Column(String)
    cause_category = Column(String)
    cause_code = Column(String)
    complete_rca_fname = Column(String)


class Five_Why_ResponseSF(BaseSF):
    __tablename__ = "FIVE_WHY_RESPONSE"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    parent_response_id = Column(Integer)
    cause = Column(String)
    reason = Column(String)


class Five_WhySF(BaseSF):
    __tablename__ = "FIVE_WHY"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    investigation_id = Column(Integer)
    root_response_id = Column(Integer)
    event_description = Column(String)
    supervisor_email = Column(String)  # comes from supervisor_id in db
    users = Column(String)


class ActionSF(BaseSF):
    __tablename__ = "ACTION"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    investigation_id = Column(Integer)
    five_why_id = Column(Integer)
    flash_report_id = Column(Integer)
    root_cause_detail_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    date_due = Column(TIMESTAMP)
    supervisor_email = Column(String)
    status = Column(String)
    date_closed = Column(TIMESTAMP)
    is_historical = Column(String)
    is_archived = Column(Boolean)
    archive_user_email = Column(String)
    archive_date_time = Column(TIMESTAMP)
    users = Column(String)
    latest_comment = Column(String)


class Charting_APLUS_SF(BaseSF):
    __tablename__ = "CHARTING_APLUS"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    equipment_id = Column(Integer)
    equipment_name = Column(String)
    start_time = Column(TIMESTAMP)
    date = Column(TIMESTAMP)  # DATE field
    effective_duration = Column(Float)
    time_usage_code = Column(String)
    problem = Column(String)
    action = Column(String)
    cause = Column(String)
    region_name = Column(String)
    area_name = Column(String)
    circuit = Column(String)


class Charting_REMS_SF(BaseSF):
    __tablename__ = "CHARTING_REMS"
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    event_id = Column(String)
    event_datetime = Column(TIMESTAMP)
    last_comment = Column(String)
    functional_location = Column(String)
    fleet_type = Column(String)
    model = Column(String)
    equipment_name = Column(String)
    site = Column(String)
    floc6 = Column(String)
    floc7 = Column(String)
    floc8 = Column(String)
    event_duration = Column(Float)


@router.patch("/push-snowflake")
def upload_bulk_snowflake(
    *,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
    merge: bool = True,
):

    # Create a DB engine
    engine = create_engine(
        "snowflake://{user}:{password}@{account_identifier}/{database_name}/{schema_name}".format(
            user=config.SNOWFLAKE_USER,
            password=config.SNOWFLAKE_PASSWORD,
            account_identifier="wn74261.ap-southeast-2",
            database_name="AA_ASSETS_FIXEDPLANT",
            schema_name="STG_DEP",
        )
    )

    try:
        # create orm session
        session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        connection = engine.connect()
        session: Session = session_local()
    except Exception as e:
        print("Error connecting to Snowflake")
        print(e)
        return

    recordsModified = 0

    # Investigation
    # Investigation - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."INVESTIGATION" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_investigation = None

    if len(items) > 0:
        lastUpdated_investigation = items[0].updated

    sInvestigation = schemas.Investigation
    if lastUpdated_investigation == None:
        investigations: List[schemas.Investigation] = db.query(sInvestigation).order_by(sInvestigation.updated).all()
    else:
        investigations: List[schemas.Investigation] = (
            db.query(sInvestigation)
            .filter(schemas.Investigation.updated > lastUpdated_investigation)
            .order_by(sInvestigation.updated)
            .all()
        )

    i = 0
    for investigation in investigations:
        supervisor_user_email = ""
        supervisor_user = crud.user.get(db, id=investigation.supervisor_id)
        if supervisor_user:
            supervisor_user_email = supervisor_user.email

        archived_user_email = ""
        if investigation.is_archived:
            archive_user = crud.user.get(db, id=investigation.archive_user_id)
            if archive_user:
                archived_user_email = archive_user.email

        # Users
        user_emails = []
        if investigation.owner_users:
            for owner_user in investigation.owner_users:
                user_emails.append(owner_user.email)

        users_emails = ", ".join(user_emails)

        # aplus_delay_event_ids
        aplus_delay_events = []
        if investigation.aplus_delay_events:
            for event in investigation.aplus_delay_events:
                aplus_delay_events.append(str(event.event_id))

        aplus_delay_events_ids = ",".join(aplus_delay_events)

        # rems_delay_event_ids
        rems_delay_events = []
        if investigation.rems_delay_events:
            for event in investigation.rems_delay_events:
                rems_delay_events.append(event.event_id)

        rems_delay_events_ids = ",".join(rems_delay_events)

        sf_investigation = InvestigationSF(
            id=investigation.id,
            created=investigation.created,
            updated=investigation.updated,
            title=investigation.title,
            description=investigation.description,
            priority=investigation.priority.name,
            investigation_type=investigation.investigation_type.name,
            event_datetime=investigation.event_datetime,
            completion_due_date=investigation.completion_due_date,
            steps_completed=investigation.steps_completed,
            function_location=investigation.function_location,
            equipment_description=investigation.equipment_description,
            object_type=investigation.object_type,
            catalog_profile=investigation.catalog_profile,
            catalog_profiles=" ".join(investigation.catalog_profiles),
            object_part_description=investigation.object_part_description,
            damage_code=investigation.damage_code,
            supervisor_email=supervisor_user_email,
            event_type=investigation.event_type.name,
            status=investigation.status.name,
            total_effective_duration=investigation.total_effective_duration,
            total_tonnes_lost=investigation.total_tonnes_lost,
            date_closed=investigation.date_closed,
            total_event_duration=investigation.total_event_duration,
            cause_code=investigation.cause_code,
            is_archived=investigation.is_archived,
            archive_user_email=archived_user_email,
            archive_datetime=investigation.archive_datetime,
            site=investigation.site,
            department=investigation.department,
            users=users_emails,
            aplus_delay_event_ids=str(aplus_delay_events_ids),
            rems_delay_event_ids=str(rems_delay_events_ids),
        )

        if merge:
            session.merge(sf_investigation)
        else:
            session.add(sf_investigation)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    '''
    # Equipment
    # Equipment - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."EQUIPMENT" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_equipment = None

    if len(items) > 0:
        lastUpdated_equipment = items[0].updated

    sEquipment = schemas.Equipment
    if lastUpdated_equipment == None:
        equipments: List[schemas.Equipment] = db.query(sEquipment).all()
    else:
        equipments: List[schemas.Equipment] = (
            db.query(sEquipment).filter(schemas.Equipment.updated > lastUpdated_equipment).all()
        )

    i = 0
    for equipment in equipments:
        sf_equipment = EquipmentSF(
            id=equipment.id,
            created=equipment.created,
            updated=equipment.updated,
            function_location=equipment.function_location,
            catalog_profile=equipment.catalog_profile,
            equipment_description=equipment.equipment_description,
            object_type=equipment.object_type,
            site=equipment.site,
            department=equipment.department,
        )

        if merge:
            session.merge(sf_equipment)
        else:
            session.add(sf_equipment)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()
    '''

    # Flash_Report
    # Flash_Report - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."FLASH_REPORT" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_flashReport = None

    if len(items) > 0:
        lastUpdated_flashReport = items[0].updated

    sFlash_Report = schemas.Flash_Report
    if lastUpdated_flashReport == None:
        flash_reports: List[schemas.Flash_Report] = db.query(sFlash_Report).order_by(sFlash_Report.updated).all()
    else:
        flash_reports: List[schemas.Flash_Report] = (
            db.query(sFlash_Report)
            .filter(schemas.Flash_Report.updated > lastUpdated_flashReport)
            .order_by(sFlash_Report.updated)
            .all()
        )

    i = 0
    for report in flash_reports:
        sf_report = Flash_ReportSF(
            id=report.id,
            created=report.created,
            updated=report.updated,
            investigation_id=report.investigation_id,
            event_title=report.event_title,
            business_impact=report.business_impact,
            immediate_action_taken=report.immediate_action_taken,
            potential_root_causes=" ".join(report.potential_root_causes),
            event_description=report.event_description,
        )

        if merge:
            session.merge(sf_report)
        else:
            session.add(sf_report)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    # Root_Cause_Detail
    # Root_Cause_Detail - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."ROOT_CAUSE_DETAIL" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_rootCauseDetail = None

    if len(items) > 0:
        lastUpdated_rootCauseDetail = items[0].updated

    sRoot_Cause_Detail = schemas.Root_Cause_Detail
    if lastUpdated_rootCauseDetail == None:
        root_cause_details: List[schemas.Root_Cause_Detail] = db.query(sRoot_Cause_Detail).order_by(sRoot_Cause_Detail.updated).all()
    else:
        root_cause_details: List[schemas.Root_Cause_Detail] = (
            db.query(sRoot_Cause_Detail)
            .filter(schemas.Root_Cause_Detail.updated > lastUpdated_rootCauseDetail)
            .order_by(sRoot_Cause_Detail.updated)
            .all()
        )

    i = 0
    for root_cause_detail in root_cause_details:
        sf_root_cause = Root_Cause_DetailSF(
            id=root_cause_detail.id,
            created=root_cause_detail.created,
            updated=root_cause_detail.updated,
            investigation_id=root_cause_detail.investigation_id,
            description=root_cause_detail.description,
            additional_contribution_factors=root_cause_detail.additional_contribution_factors,
            cause_category=root_cause_detail.cause_category,
            cause_code=root_cause_detail.cause_code,
            complete_rca_fname=root_cause_detail.complete_rca_fname,
        )

        if merge:
            session.merge(sf_root_cause)
        else:
            session.add(sf_root_cause)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    # Five_Why_Response
    # Five_Why_Response - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."FIVE_WHY_RESPONSE" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_fiveWhyResponse = None

    if len(items) > 0:
        lastUpdated_fiveWhyResponse = items[0].updated

    sFive_Why_Response = schemas.Five_Why_Response
    if lastUpdated_fiveWhyResponse == None:
        five_why_responses: List[schemas.Five_Why_Response] = db.query(sFive_Why_Response).order_by(sFive_Why_Response.updated).all()
    else:
        five_why_responses: List[schemas.Five_Why_Response] = (
            db.query(sFive_Why_Response)
            .filter(schemas.Five_Why_Response.updated > lastUpdated_fiveWhyResponse)
            .order_by(sFive_Why_Response.updated)
            .all()
        )

    i = 0
    for five_why_response in five_why_responses:
        sf_five_why_response = Five_Why_ResponseSF(
            id=five_why_response.id,
            created=five_why_response.created,
            updated=five_why_response.updated,
            parent_response_id=five_why_response.parent_response_id,
            cause=five_why_response.cause,
            reason=five_why_response.reason,
        )

        if merge:
            session.merge(sf_five_why_response)
        else:
            session.add(sf_five_why_response)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    # Five_Why
    # Five_Why - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."FIVE_WHY" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_fiveWhy = None

    if len(items) > 0:
        lastUpdated_fiveWhy = items[0].updated

    sFive_Why = schemas.Five_Why
    if lastUpdated_fiveWhy == None:
        five_whys: List[schemas.Five_Why] = db.query(sFive_Why).order_by(sFive_Why.updated).all()
    else:
        five_whys: List[schemas.Five_Why] = (
            db.query(sFive_Why).filter(schemas.Five_Why.updated > lastUpdated_fiveWhy).order_by(sFive_Why.updated).all()
        )

    i = 0
    for five_why in five_whys:
        supervisor_user_email = ""
        supervisor_user = crud.user.get(db, id=five_why.supervisor_id)
        if supervisor_user:
            supervisor_user_email = supervisor_user.email

        # Users
        user_emails = []
        if five_why.owner_users:
            for owner_user in five_why.owner_users:
                user_emails.append(owner_user.email)

        users_emails = ", ".join(user_emails)

        sf_five_why = Five_WhySF(
            id=five_why.id,
            created=five_why.created,
            updated=five_why.updated,
            investigation_id=five_why.investigation_id,
            root_response_id=five_why.root_response_id,
            event_description=five_why.event_description,
            supervisor_email=supervisor_user_email,
            users=users_emails,
        )

        if merge:
            session.merge(sf_five_why)
        else:
            session.add(sf_five_why)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    # Action
    # Action - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."ACTION" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_action = None

    if len(items) > 0:
        lastUpdated_action = items[0].updated

    sAction = schemas.Action
    if lastUpdated_action == None:
        actions: List[schemas.Action] = db.query(sAction).order_by(sAction.updated).all()
    else:
        actions: List[schemas.Action] = (
            db.query(sAction).filter(schemas.Action.updated > lastUpdated_action).order_by(sAction.updated).all()
        )

    i = 0
    for action in actions:
        supervisor_user_email = ""
        supervisor_user = crud.user.get(db, id=action.supervisor_id)
        if supervisor_user:
            supervisor_user_email = supervisor_user.email

        archived_user_email = ""
        if action.is_archived:
            archive_user = crud.user.get(db, id=action.archive_user_id)
            if archive_user:
                archived_user_email = archive_user.email

        # Users
        user_emails = []
        if action.owner_users:
            for owner_user in action.owner_users:
                user_emails.append(owner_user.email)

        users_emails = ", ".join(user_emails)

        # latest_comment
        latestComment = ""
        latestCommentUpdated = None

        if action.comments:
            for comment in action.comments:
                if latestCommentUpdated == None or comment.updated >= latestCommentUpdated:
                    latestCommentUpdated = comment.updated
                    latestComment = comment.comment

        sf_action = ActionSF(
            id=action.id,
            created=action.created,
            updated=action.updated,
            investigation_id=action.investigation_id,
            five_why_id=action.five_why_id,
            flash_report_id=action.flash_report_id,
            root_cause_detail_id=action.root_cause_detail_id,
            title=action.title,
            description=action.description,
            priority=action.priority.name,  # enum
            date_due=action.date_due,
            supervisor_email=supervisor_user_email,
            status=action.status.name,  # enum
            date_closed=action.date_closed,
            is_historical=action.is_historical.name,
            is_archived=action.is_archived,
            archive_user_email=archived_user_email,
            archive_date_time=action.archive_datetime,
            users=users_emails,
            latest_comment=latestComment,
        )

        if merge:
            session.merge(sf_action)
        else:
            session.add(sf_action)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    '''
    # Charting_Aplus
    # Charting_Aplus - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."CHARTING_APLUS" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_chartingAPLUS = None

    if len(items) > 0:
        lastUpdated_chartingAPLUS = items[0].updated

    sCharting_Aplus = schemas.Charting
    if lastUpdated_chartingAPLUS == None:
        aplus_charts: List[schemas.Charting] = db.query(sCharting_Aplus).all()
    else:
        aplus_charts: List[schemas.Charting] = (
            db.query(sCharting_Aplus)
            .filter(schemas.Charting.updated > lastUpdated_chartingAPLUS)
            .all()
        )

    # aplus_charts: List[schemas.Charting] = db.query(sCharting_Aplus).limit(500)

    i = 0
    for chart in aplus_charts:
        sf_chart_aplus = Charting_APLUS_SF(
            id=chart.id,
            created=chart.created,
            updated=chart.updated,
            equipment_id=chart.equipment_id,
            equipment_name=chart.equipment_name,
            start_time=chart.start_time,
            date=chart.date,
            effective_duration=chart.effective_duration,
            time_usage_code=chart.time_usage_code.name,
            problem=chart.problem,
            action=chart.action,
            cause=chart.cause,
            region_name=chart.region_name,
            area_name=chart.area_name,
            circuit=chart.circuit,
        )

        if merge:
            session.merge(sf_chart_aplus)
        else:
            session.add(sf_chart_aplus)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()

    # Charting_Rems
    # Charting_Rems - SF - Get latest updated time
    sql = """ SELECT * FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."CHARTING_REMS" ORDER BY UPDATED DESC LIMIT 1 """
    items = sf.execute(sql).fetchall()
    lastUpdated_chartingREMS = None

    if len(items) > 0:
        lastUpdated_chartingREMS = items[0].updated

    sCharting_Rems = schemas.ChartingREMS
    if lastUpdated_chartingREMS == None:
        rems_charts: List[schemas.ChartingREMS] = db.query(sCharting_Rems).all()
    else:
        rems_charts: List[schemas.ChartingREMS] = (
            db.query(sCharting_Rems)
            .filter(schemas.ChartingREMS.updated > lastUpdated_chartingREMS)
            .all()
        )

    i = 0
    for chart in rems_charts:
        sf_chart_rems = Charting_REMS_SF(
            id=chart.id,
            created=chart.created,
            updated=chart.updated,
            event_id=chart.event_id,
            event_datetime=chart.event_datetime,
            last_comment=chart.last_comment,
            functional_location=chart.functional_location,
            fleet_type=chart.fleet_type,
            model=chart.model,
            equipment_name=chart.equipment_name,
            site=chart.site,
            floc6=chart.floc6,
            floc7=chart.floc7,
            floc8=chart.floc8,
            event_duration=chart.event_duration,
        )

        if merge:
            session.merge(sf_chart_rems)
        else:
            session.add(sf_chart_rems)

        i += 1
        if i > 2000:
            session.commit()
            i = 0

        recordsModified = recordsModified + 1

    session.commit()
    '''

    connection.close()
    session.close()

    print("-------- SNOWFLAKE EXPORT -------- Total records created/modified: ", recordsModified)


@router.patch("/clean-snowflake")
def clean_snowflake_duplicates(
    *, db=Depends(utils.get_db), sf=Depends(utils.get_sf_db), valid=Depends(utils.token_auth)
):
    # Create a DB engine
    engine = create_engine(
        "snowflake://{user}:{password}@{account_identifier}/{database_name}/{schema_name}".format(
            user=config.SNOWFLAKE_USER,
            password=config.SNOWFLAKE_PASSWORD,
            account_identifier="wn74261.ap-southeast-2",
            database_name="AA_ASSETS_FIXEDPLANT",
            schema_name="STG_DEP",
        )
    )

    try:
        # create orm session
        session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        connection = engine.connect()
        session: Session = session_local()
    except Exception as e:
        print("Error connecting to Snowflake")
        print(e)
        return

    def getSchema(tableName):
        if tableName == "ACTION":
            return schemas.Action
        if tableName == "INVESTIGATION":
            return schemas.Investigation
        if tableName == "FLASH_REPORT":
            return schemas.Flash_Report
        if tableName == "ROOT_CAUSE_DETAIL":
            return schemas.Root_Cause_Detail
        if tableName == "FIVE_WHY_RESPONSE":
            return schemas.Five_Why_Response
        if tableName == "FIVE_WHY":
            return schemas.Five_Why

        return None

    def buildModel(tableName, resultObject):
        if tableName == "ACTION":
            supervisor_user_email = ""
            supervisor_user = crud.user.get(db, id=resultObject.supervisor_id)
            if supervisor_user:
                supervisor_user_email = supervisor_user.email

            archived_user_email = ""
            if resultObject.is_archived:
                archive_user = crud.user.get(db, id=resultObject.archive_user_id)
                if archive_user:
                    archived_user_email = archive_user.email

            # Users
            user_emails = []
            if resultObject.owner_users:
                for owner_user in resultObject.owner_users:
                    user_emails.append(owner_user.email)

            users_emails = ", ".join(user_emails)

            # latest_comment
            latestComment = ""
            latestCommentUpdated = None

            if resultObject.comments:
                for comment in resultObject.comments:
                    if latestCommentUpdated == None or comment.updated >= latestCommentUpdated:
                        latestCommentUpdated = comment.updated
                        latestComment = comment.comment
            sf_action = ActionSF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                investigation_id=resultObject.investigation_id,
                five_why_id=resultObject.five_why_id,
                flash_report_id=resultObject.flash_report_id,
                root_cause_detail_id=resultObject.root_cause_detail_id,
                title=resultObject.title,
                description=resultObject.description,
                priority=resultObject.priority.name,  # enum
                date_due=resultObject.date_due,
                supervisor_email=supervisor_user_email,
                status=resultObject.status.name,  # enum
                date_closed=resultObject.date_closed,
                is_historical=resultObject.is_historical.name,
                is_archived=resultObject.is_archived,
                archive_user_email=archived_user_email,
                archive_date_time=resultObject.archive_datetime,
                users=users_emails,
                latest_comment=latestComment,
            )
            return sf_action

        if tableName == "INVESTIGATION":
            supervisor_user_email = ""
            supervisor_user = crud.user.get(db, id=resultObject.supervisor_id)
            if supervisor_user:
                supervisor_user_email = supervisor_user.email

            archived_user_email = ""
            if resultObject.is_archived:
                archive_user = crud.user.get(db, id=resultObject.archive_user_id)
                if archive_user:
                    archived_user_email = archive_user.email

            # Users
            user_emails = []
            if resultObject.owner_users:
                for owner_user in resultObject.owner_users:
                    user_emails.append(owner_user.email)

            users_emails = ", ".join(user_emails)

            # aplus_delay_event_ids
            aplus_delay_events = []
            if resultObject.aplus_delay_events:
                for event in resultObject.aplus_delay_events:
                    aplus_delay_events.append(str(event.event_id))

            aplus_delay_events_ids = ",".join(aplus_delay_events)

            # rems_delay_event_ids
            rems_delay_events = []
            if resultObject.rems_delay_events:
                for event in resultObject.rems_delay_events:
                    rems_delay_events.append(event.event_id)

            rems_delay_events_ids = ",".join(rems_delay_events)

            sf_investigation = InvestigationSF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                title=resultObject.title,
                description=resultObject.description,
                priority=resultObject.priority.name,
                investigation_type=resultObject.investigation_type.name,
                event_datetime=resultObject.event_datetime,
                completion_due_date=resultObject.completion_due_date,
                steps_completed=resultObject.steps_completed,
                function_location=resultObject.function_location,
                equipment_description=resultObject.equipment_description,
                object_type=resultObject.object_type,
                catalog_profile=resultObject.catalog_profile,
                catalog_profiles=" ".join(resultObject.catalog_profiles),
                object_part_description=resultObject.object_part_description,
                damage_code=resultObject.damage_code,
                supervisor_email=supervisor_user_email,
                event_type=resultObject.event_type.name,
                status=resultObject.status.name,
                total_effective_duration=resultObject.total_effective_duration,
                total_tonnes_lost=resultObject.total_tonnes_lost,
                date_closed=resultObject.date_closed,
                total_event_duration=resultObject.total_event_duration,
                cause_code=resultObject.cause_code,
                is_archived=resultObject.is_archived,
                archive_user_email=archived_user_email,
                archive_datetime=resultObject.archive_datetime,
                site=resultObject.site,
                department=resultObject.department,
                users=users_emails,
                aplus_delay_event_ids=str(aplus_delay_events_ids),
                rems_delay_event_ids=str(rems_delay_events_ids),
            )
            return sf_investigation

        if tableName == "FLASH_REPORT":
            sf_report = Flash_ReportSF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                investigation_id=resultObject.investigation_id,
                event_title=resultObject.event_title,
                business_impact=resultObject.business_impact,
                immediate_action_taken=resultObject.immediate_action_taken,
                potential_root_causes=" ".join(resultObject.potential_root_causes),
                event_description=resultObject.event_description,
            )
            return sf_report

        if tableName == "ROOT_CAUSE_DETAIL":
            sf_root_cause = Root_Cause_DetailSF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                investigation_id=resultObject.investigation_id,
                description=resultObject.description,
                additional_contribution_factors=resultObject.additional_contribution_factors,
                cause_category=resultObject.cause_category,
                cause_code=resultObject.cause_code,
                complete_rca_fname=resultObject.complete_rca_fname,
            )
            return sf_root_cause
        
        if tableName == "FIVE_WHY_RESPONSE":
            sf_five_why_response = Five_Why_ResponseSF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                parent_response_id=resultObject.parent_response_id,
                cause=resultObject.cause,
                reason=resultObject.reason,
            )
            return sf_five_why_response
        
        if tableName == "FIVE_WHY":
            supervisor_user_email = ""
            supervisor_user = crud.user.get(db, id=resultObject.supervisor_id)
            if supervisor_user:
                supervisor_user_email = supervisor_user.email

            # Users
            user_emails = []
            if resultObject.owner_users:
                for owner_user in resultObject.owner_users:
                    user_emails.append(owner_user.email)

            users_emails = ", ".join(user_emails)

            sf_five_why = Five_WhySF(
                id=resultObject.id,
                created=resultObject.created,
                updated=resultObject.updated,
                investigation_id=resultObject.investigation_id,
                root_response_id=resultObject.root_response_id,
                event_description=resultObject.event_description,
                supervisor_email=supervisor_user_email,
                users=users_emails,
            )
            return sf_five_why

        return None

    tableNames = ["ACTION", "INVESTIGATION", "FLASH_REPORT", "ROOT_CAUSE_DETAIL", "FIVE_WHY_RESPONSE", "FIVE_WHY"]

    for table in tableNames:
        sql = """ SELECT id FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."{}" GROUP BY ID HAVING COUNT(*) > 1 """.format(
            table
        )
        items = sf.execute(sql).fetchall()
        ids = [item.id for item in items]
        sql = """ DELETE FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."{}" WHERE """.format(table)

        for id in ids:
            sql = """ DELETE FROM "AA_ASSETS_FIXEDPLANT"."STG_DEP"."{}" WHERE {}.id={} """.format(
                table, table, id
            )
            session.execute(sql)
            session.commit()

        schema = getSchema(table)
        records: List[schema] = db.query(schema).filter(schema.id.in_(ids)).all()

        i = 0
        for record in records:
            sf_record = buildModel(table, record)
            session.add(sf_record)
            i += 1
            if i > 2000:
                session.commit()
                i = 0

        session.commit()
