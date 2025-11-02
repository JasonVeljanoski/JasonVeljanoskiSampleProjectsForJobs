import datetime as dt
import logging
import uuid

import pytz
from fastapi import APIRouter, BackgroundTasks, Depends

from app import crud, schemas, utils
from app.utils import redis_helper

from .action_ingestion import *

utc = pytz.UTC
router = APIRouter()

logger = logging.getLogger(__name__)


# ----------------------------------------------------

# RUN ONCE TASKS
@router.post("/redis_equipment_ingest")
def redis_equipment_ingest(
    *,
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    """ """
    query = """
        SELECT 
        CASE WHEN LEN("FLOC"."functional_location") = 17 THEN CONCAT("FLOC"."functional_location",' ')
        WHEN LEN("FLOC"."functional_location") = 24 THEN CONCAT("FLOC"."functional_location",' ')
        ELSE "FLOC"."functional_location"
        END as "functional_location", 
        "FLOC"."catalog_profile",
        "FLOC"."equipment_description",
        "FLOC"."object_type",
        "Site"."Description" as "site",
                CASE WHEN "FLOC"."functional_location" LIKE '%-WTRS-%' THEN 'Dewatering'
                ELSE "Department"."Description" END as "department"
                FROM
                (
            Select  "FunctionalLocation"."FunctionalLocation" as "floc_id",
                        "FunctionalLocation"."FunctionalLocationLabel" as "functional_location",
                        CASE WHEN "EquipmentCurrent"."EquipmentDescription" IS NOT NULL THEN "EquipmentCurrent"."EquipmentDescription"
                        ELSE "FunctionalLocation"."FunctionalLocationDescription" END as "equipment_description",
                        CASE WHEN "FunctionalLocation"."TechnicalObjectTypeDescription" IS NOT NULL THEN "FunctionalLocation"."TechnicalObjectTypeDescription"
                        ELSE 'Unknown Object' END as "object_type",
                        "FunctionalLocation"."CatalogProfile" as "catalog_profile"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
                LEFT OUTER JOIN (SELECT * FROM
                "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."EquipmentCurrent" 
                WHERE "EquipmentCurrent"."EffectiveToDate" > CURRENT_DATE) "EquipmentCurrent"
                ON "EquipmentCurrent"."FunctionalLocation" = "FunctionalLocation"."FunctionalLocation"
                WHERE  "FunctionalLocation"."EffectiveToDate" > CURRENT_DATE
                AND "FunctionalLocation"."FunctionalLocationLabel" LIKE '___-__-____-%'
                AND "FunctionalLocation"."FunctionalLocationLabel" LIKE '___-MP%'
                
                ) "FLOC"

                LEFT OUTER JOIN
                (Select "FunctionalLocationLabel" as "functional_location",
                "FunctionalLocationDescription" as "Description"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
                WHERE "FunctionalLocationLabel" LIKE '___-__'
                AND "EffectiveToDate" > CURRENT_DATE
                ) "Department" ON "Department"."functional_location" = left("FLOC"."functional_location",6)
                
                LEFT OUTER JOIN 
                (Select "FunctionalLocationLabel" as "functional_location",
                "FunctionalLocationDescription" as "Description"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
                WHERE "FunctionalLocationLabel" LIKE '___'
                AND "EffectiveToDate" > CURRENT_DATE
                ) "Site" ON "Site"."functional_location" = left("FLOC"."functional_location",3)
                WHERE "Department"."Description" != 'Non Process Infrastructure'
                AND "FLOC"."functional_location" LIKE '___-MP%'
                
                UNION
                
                SELECT  
        CASE WHEN LEN("FLOC"."functional_location") = 17 THEN CONCAT("FLOC"."functional_location",' ')
        WHEN LEN("FLOC"."functional_location") = 24 THEN CONCAT("FLOC"."functional_location",' ')
        ELSE "FLOC"."functional_location"
        END as "functional_location",
                "FLOC"."catalog_profile",
                "FLOC"."equipment_description",
                "FLOC"."object_type",
                "Site"."Description" as "site",
                CASE WHEN "FLOC"."functional_location" LIKE '%-WTRS-%' THEN 'Dewatering'
                ELSE "Department"."Description" END "department"
                FROM
                (
                Select "FunctionalLocationLabel" as "functional_location",
                "EquipmentDescription" as "equipment_description",
                "TechnicalObjectTypeDescription" as "object_type",
                "CatalogProfile" as "catalog_profile"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."EquipmentCurrent"
                WHERE "FunctionalLocationLabel" LIKE '___-__-____-%'
                AND "FunctionalLocationLabel" NOT LIKE '___-MP%'
                AND "EffectiveToDate" > CURRENT_DATE
                ) "FLOC"

                LEFT OUTER JOIN 
                (Select "FunctionalLocationLabel" as "functional_location",
                "LocationDescription" as "Description"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
                WHERE "FunctionalLocationLabel" LIKE '___-__'
                AND "EffectiveToDate" > CURRENT_DATE
                ) "Department" ON "Department"."functional_location" = left("FLOC"."functional_location",6)
                
                LEFT OUTER JOIN 
                (Select "FunctionalLocationLabel" as "functional_location",
                "FunctionalLocationDescription" as "Description"

                from "AA_ASSETS_MAINTENANCESYSTEMS"."QUERY"."FunctionalLocation"
                WHERE "FunctionalLocationLabel" LIKE '___'
                AND "EffectiveToDate" > CURRENT_DATE
                ) "Site" ON "Site"."functional_location" = left("FLOC"."functional_location",3)
    """

    def pad_floc(floc_str):
        """
        Force floc length policy on floc strings
        Cannot trust data
        """
        FLOC_LENGTHS = [3, 2, 4, 6, 6, 5, 5]  # standard policy for floc length
        keys = floc_str.split("-")
        padded_floc = []

        for ii in range(len(keys)):
            key = keys[ii]
            floc_len = FLOC_LENGTHS[ii]
            key_len = len(key)

            if key_len < floc_len:
                key += " " * (floc_len - key_len)

            padded_floc.append(key)

        return "-".join(padded_floc)

    result = db_sf.execute(query).mappings().all()
    full_flocs = [pad_floc(floc["functional_location"]) for floc in result]

    redis_db = redis_helper.Redis_Client()

    # longest floc
    max = 0
    for floc in full_flocs:
        length = len(floc.split("-"))
        if max < length:
            max = length

    # ---------

    MAX_DEPTHS = [1, 2, 3, 4, 5, 6, 7]

    floc_perms = []
    for floc in full_flocs:
        for depth in MAX_DEPTHS:
            temp = "-".join(floc.split("-")[:depth])

            # no duplicates
            if temp not in floc_perms:
                floc_perms.append(temp)

    # ---------

    redis_db.set("floc_perms", json.dumps(floc_perms))


# -----------------------------------------------------------------------------------


def redis_my_team():
    db = next(utils.get_db())
    db_sf = next(utils.get_sf())

    sql = """
        SELECT  
            "SupervisorEmail", "EmployeeEmail", "SuperTier"
        FROM 
            AA_ASSETS_FIXEDPLANT.SELFSERVICE."ap_SupervisorTeams"
        WHERE 
            "SupervisorEmail" is not NULL and "EmployeeEmail" is not NULL and "SupervisorEmail" != "EmployeeEmail"
    """

    items = db_sf.execute(sql).fetchall()

    logger.info(f"Found {len(items)} items")

    res = {}
    try:
        for item in items:

            supervisor = crud.user.get_kw_single(db, email=item.SupervisorEmail.lower())
            employee = crud.user.get_kw_single(db, email=item.EmployeeEmail.lower())

            # update supervisor
            if supervisor and employee:
                # filter items by employee email
                filtered_items = [i for i in items if i.EmployeeEmail == item.EmployeeEmail.lower()]
                # get row with highest tier
                filtered_items = sorted(filtered_items, key=lambda x: x.SuperTier, reverse=True)
                # get supervisor email
                supervisor_email = filtered_items[0].SupervisorEmail
                immediate_supervisor = crud.user.get_kw_single(db, email=supervisor_email.lower())

                if immediate_supervisor:
                    employee.supervisor_id = immediate_supervisor.id
                    db.commit()

            if supervisor and employee:
                if supervisor.id not in res or not res[supervisor.id]:
                    res[supervisor.id] = []

                res[supervisor.id].append(
                    {
                        "user_id": employee.id,
                        "email": employee.email,
                        "functional_locations": employee.functional_locations
                        if employee.functional_locations
                        else [],
                        "work_centers": employee.work_centers if employee.work_centers else [],
                    }
                )
    except Exception as e:
        logger.exception(e)

    redis_db = redis_helper.Redis_Client()
    redis_db.set("user_teams", json.dumps(res))

    db.close()
    db_sf.close()


@router.post("/redis_my_team")
async def redis_my_team_task(
    background_tasks: BackgroundTasks,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    background_tasks.add_task(redis_my_team)
    return {"message": "Building redis my team list in background"}


# -----------------------------------------------------------------------------------


@router.post("/redis_workcentres_ingest")
def redis_workcentres_ingest(
    *,
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    sql = """
    SELECT 
        "WorkCentre", "Description" 
    FROM 
        "EDW"."SELFSERVICE"."WorkCentre"
    """

    items = db_sf.execute(sql).fetchall()

    res = []
    for item in items:
        res.append({"workcenter": item[0], "description": f"({item[0]}) {item[1]}"})

    # remove duplicate workcenters from list of dicts
    res = [dict(t) for t in {tuple(d.items()) for d in res}]

    redis_db = redis_helper.Redis_Client()
    redis_db.set("workcenters", json.dumps(res))


# --------------------------------------------------------------------------------------------


@router.post("/redis_init")
def redis_init(
    *,
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    redis_equipment_ingest(db_sf=db_sf, valid=valid)
    redis_workcentres_ingest(db_sf=db_sf, valid=valid)


# --------------------------------------------------------------------------------------------
# TIMER TASKS


@router.post("/set_overdue_actions")
def set_overdue_actions(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    open_actions = crud.action.get_kw(db, status=schemas.StatusEnum.OPEN)
    time = utc.localize(dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    for action in open_actions:
        if action.date_due and action.date_due < time:
            action.status = schemas.StatusEnum.OVERDUE
            db.add(action)
            db.commit()


@router.post("/update_users")
def refresh_user(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):

    query = """
        SELECT 
            CONCAT(
                COALESCE("PreferredName","FirstName"), 
                ' ',
                INITCAP("LastName") 
            ) as "name",
            LOWER("Email") as "email",
            "JobTitle" as "position",
            "Employee_BK" as "sap_id", 
            "Key_Employee_Supervisor" as "supervisor_sap_id" 
        FROM "EDW"."SELFSERVICE"."Employee"
        WHERE "TerminationDate" > CURRENT_TIMESTAMP
            AND "Email" IS NOT NULL
            AND "PositionStatus" = 'Current'
    """
    results = db_sf.execute(query).mappings().all()

    for r in results:

        email_user = crud.user.get_kw_single(db, email=r["email"].lower())
        sap_user = crud.user.get_kw_single(db, sap_number=int(r["sap_id"]))
        email_sap_user = crud.user.get_kw_single(
            db, email=r["email"].lower(), sap_number=int(r["sap_id"])
        )

        # user exists in db
        if email_user or sap_user or email_sap_user:

            if email_sap_user:
                db.merge(
                    schemas.User(
                        id=email_sap_user.id,
                        name=r["name"],
                        email=r["email"],
                        job_title=r["position"],
                        sap_number=int(r["sap_id"]),
                    )
                )
            elif email_user or sap_user:
                db.merge(
                    schemas.User(
                        id=email_user.id if email_user else sap_user.id,
                        name=r["name"],
                        email=r["email"],
                        job_title=r["position"],
                        sap_number=int(r["sap_id"]),
                    )
                )
        # new user
        else:
            db.add(
                schemas.User(
                    name=r["name"],
                    email=r["email"],
                    job_title=r["position"],
                    sap_number=int(r["sap_id"]),
                )
            )

        db.commit()


@router.patch("/archive_closed_actions")
def auto_archived_closed(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    thirty_days_ago = dt.datetime.now() - dt.timedelta(days=30)

    actions = (
        db.query(schemas.Action)
        .filter(
            schemas.Action.is_archived == False,
            schemas.Action.status == schemas.StatusEnum.CLOSED,
            schemas.Action.date_closed < thirty_days_ago,
        )
        .all()
    )

    count = 0
    for action in actions:
        action.is_archived = True
        count += 1

    db.commit()

    return {"message": f"{count} actions archived"}


# --------------------------------------------------------------------------------------------


@router.post("/daily_action_ingest")
async def daily_action_ingest(
    *,
    db=Depends(utils.get_db),
    sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    syncUUID = str(uuid.uuid4())

    # Methods will return stats - Return # of actions created, updated, archived
    # stats = [numCreated, numUpdated, numArchived]

    total_created = 0
    total_updated = 0
    total_archived = 0

    print("============> SAP NOTI Actions Ingested - Started")
    result = await sap_notification(db=db, sf=sf, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> SAP NOTI Actions Ingested - Finished")

    print("============> SAP WO Actions Ingested - Started")
    result = await get_sap_work_orders(db=db, sf=sf, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> SAP WO Actions Ingested - Finished")

    print("============> SMH Actions Ingested - Started")
    result = await smh(db=db, sf=sf, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> SMH Actions Ingested - Finished")

    print("============> AHM Actions Ingested - Started")
    result = await ahm(db=db, sf=sf, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> AHM Actions Ingested - Finished")

    print("============> DEP Actions Ingested - Started")
    result = await dep(db=db, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> DEP Actions Ingested - Finished")

    print("============> BMS Actions Ingested - Started")
    result = await bms(db=db, sf=sf, valid=valid, syncUUID=syncUUID)
    total_created = total_created + result[0]
    total_updated = total_updated + result[1]
    total_archived = total_archived + result[2]
    print("============> BMS Actions Ingested - Finished")

    # Create Ingestion Sync Log for this sync
    crud.log.create_ingestion_log(db, syncUUID, total_created, total_archived, total_updated)
