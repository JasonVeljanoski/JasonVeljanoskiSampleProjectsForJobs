from math import ceil

from fastapi import APIRouter, Depends
from sqlalchemy import func

from app import crud, schemas, utils

router = APIRouter()

# ------------------
# READ
# ------------------


@router.post("/aplus_event_details")
def get_aplus_event_details(
    *,
    db_sf=Depends(utils.get_sf_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    aplus_event_ids: list[str],
):
    ids = ""
    for x in aplus_event_ids:
        ids += f"{x},"
    ids = ids[:-1]

    q = f"""
        SELECT
            CASE WHEN "EffectiveDuration" IS NOT NULL THEN "EffectiveDuration"
            ELSE 0
            END "EffectiveDuration",
            CASE WHEN "TonnesLoss" IS NOT NULL THEN "TonnesLoss"
            ELSE 0
            END "TonnesLoss",
            CASE WHEN "EventDuration" IS NOT NULL THEN "EventDuration"
            ELSE 0
            END "EventDuration"
            FROM (
            SELECT
            ROUND( SUM(CASE WHEN "EffectiveDuration" IS NOT NULL THEN "EffectiveDuration"/3600
            WHEN "DurationSeconds" IS NOT NULL THEN "DurationSeconds"/3600 
            ELSE 0
            END ),1)"EffectiveDuration",
            ROUND(SUM(CASE WHEN "TonnesLoss" IS NOT NULL THEN "TonnesLoss" 
            ELSE 0 
            END),1) "TonnesLoss",
            ROUND(SUM(CASE WHEN "DurationSeconds" IS NOT NULL THEN "DurationSeconds"/3600 
            ELSE 0 
            END),1) "EventDuration"

            FROM "EDW"."SELFSERVICE"."APLUS_vwEventAllocation" 
            WHERE "Id" IN ({ids})
            ) "aplus_return"
    """

    result = db_sf.execute(q).mappings().all()
    return result[0]


@router.post("/rems_event_details")
def get_rems_event_details(
    *,
    db_sf=Depends(utils.get_sf_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    rems_event_ids: list[str],
):
    ids = ""
    for x in rems_event_ids:
        ids += f"'{x}',"
    ids = ids[:-1]

    q = f"""
    SELECT 
        IFNULL(
        SUM(
        CASE WHEN "EventClosedDateTime" IS NOT NULL THEN DATEDIFF(sec,"EventDateTime", "EventClosedDateTime")/3600
        WHEN "SystemClosedDate" IS NOT NULL THEN DATEDIFF(sec,"EventDateTime", "SystemClosedDate")/3600
        WHEN DATEDIFF(sec,"EventDateTime", CURRENT_TIMESTAMP)/3600 IS NOT NULL THEN DATEDIFF(sec,"EventDateTime", CURRENT_TIMESTAMP)/3600
        ELSE 0
        END )
        ,0) "duration"
        FROM "EDW"."STG_REMS"."Event"
        WHERE "EventID" IN ({ids})
        AND "Event"."DeletionFlag" = FALSE AND "Event"."EffectiveToDate" IS NULL
    """

    result = db_sf.execute(q).mappings().all()
    return result[0]


@router.get("/damage_codes")
def get_damage_codes(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    DAMAGE = "Overview of Damage"

    damage_codes = (
        db.query(schemas.Object_Code.object_description)
        .filter(schemas.Object_Code.catalog == DAMAGE)
        .order_by(schemas.Object_Code.object_description)
        .distinct()
    )

    return [x for x, in damage_codes]


@router.get("/cause_codes")
def get_cause_codes(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    CAUSE = "Causes"

    causes = (
        db.query(schemas.Object_Code.object_description)
        .filter(schemas.Object_Code.catalog == CAUSE)
        .order_by(schemas.Object_Code.object_description)
        .distinct()
    )

    return [x for x, in causes]


@router.get("/function_locations")
def get_function_locations(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.equipment.get_distinct(db, schemas.Equipment.function_location)


@router.get("/sites")
def get_sites(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.equipment.get_distinct(db, schemas.Equipment.site)


@router.get("/departments")
def get_departments(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.equipment.get_distinct(db, schemas.Equipment.department)


@router.get("/equipments")
def get_equipments(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.equipment.get_distinct(db, schemas.Equipment.equipment_description)


@router.get("/object_types")
def get_object_types(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.equipment.get_distinct(db, schemas.Equipment.object_type)


@router.get("/object_parts")
def get_object_parts(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.object_code.get_distinct(db, schemas.Object_Code.object_description)


@router.get("/max_total_effective_duration")
def get_max_total_effective_duration(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    max_duration = db.query(
        func.coalesce(func.max(schemas.Investigation.total_event_duration), 0)
    ).scalar()

    max_effective_duration = db.query(
        func.coalesce(func.max(schemas.Investigation.total_effective_duration), 0)
    ).scalar()

    return {
        "max_duration": ceil(max_duration),
        "max_effective_duration": ceil(max_effective_duration),
    }


# ---------------------------------------


@router.get("/filter_equipment_by_function_locations")
def filter_equipment_by_function_locations(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    function_location: str,
):
    return crud.equipment.get_kw(db, function_location=function_location)


@router.get("/filter_function_locations_by_equipment")
def filter_function_locations_by_equipment(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    equipment: str,
):
    return crud.equipment.get_kw(db, equipment_description=equipment)


@router.get("/default_object_type_and_cat_profile")
def get_default_object_type_and_cat_profile(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    function_location: str,
    equipment_description: str,
):
    unique_equipment = crud.equipment.get_kw(
        db, function_location=function_location, equipment_description=equipment_description
    )

    # object type classification methodology specifies a unique result here
    if len(unique_equipment) != 1:
        raise utils.errors.CustomException

    unique_equipment = unique_equipment[0]

    return dict(
        object_type=unique_equipment.object_type,
        catalog_profile=unique_equipment.catalog_profile,
        site=unique_equipment.site,
        department=unique_equipment.department,
    )


@router.get("/filtered_cat_profiles_by_object_type")
def get_filtered_object_types_and_cat_profiles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    object_type: str,
):
    res = (
        db.query(schemas.Equipment)
        .filter(schemas.Equipment.object_type == object_type)
        .order_by(schemas.Equipment.catalog_profile)
    )
    return list(set(x.catalog_profile for x in res if x.catalog_profile))


@router.post("/objects_and_damages_by_catalog_profiles")
def get_objects_and_damages_by_catalog_profiles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    catalog_profiles: list[str],
):
    OBJECT_PART = "Object Parts"
    DAMAGE = "Overview of Damage"

    object_parts = (
        db.query(schemas.Object_Code)
        .filter(schemas.Object_Code.catalog == OBJECT_PART)
        .filter(schemas.Object_Code.cat_prof_code.in_(catalog_profiles))
        .order_by(schemas.Object_Code.object_description)
        .all()
    )

    damage_codes = (
        db.query(schemas.Object_Code)
        .filter(schemas.Object_Code.catalog == DAMAGE)
        .filter(schemas.Object_Code.cat_prof_code.in_(catalog_profiles))
        .order_by(schemas.Object_Code.object_description)
        .all()
    )

    return dict(
        object_parts=[x.object_description for x in object_parts],
        damage_codes=[x.object_description for x in damage_codes],
    )


@router.post("/causes_by_catalog_profiles")
def get_causes_by_catalog_profiles(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    catalog_profiles: list[str],
):
    CAUSE = "Causes"

    causes = (
        db.query(schemas.Object_Code)
        .filter(schemas.Object_Code.catalog == CAUSE)
        .filter(schemas.Object_Code.cat_prof_code.in_(catalog_profiles))
        .order_by(schemas.Object_Code.object_description)
        .all()
    )

    return [x.object_description for x in causes]
