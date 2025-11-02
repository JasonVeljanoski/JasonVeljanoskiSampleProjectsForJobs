import csv
import json

from app import crud, redis, schemas, utils
from fastapi import APIRouter, Depends

router = APIRouter()


# ------------------
# CREATE
# ------------------

# RUN ONCE TASKS
# --------------------------------------------------------------------------------


@router.post("/defect_codes")
def ingest_defect_codes(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    """
    RUN ONCE - populate schemas.Object_Code
    read from .csv --> change later to snowflake query to get most up to date data
    """
    csv_file_name = "defect_codes.csv"
    full_path = f"/app/app/ingest/{csv_file_name}"

    crud.object_code.delete_all(db)

    with open(full_path, encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)

        for r in rows:
            db.add(
                schemas.Object_Code(
                    cat_prof_code=r.get("Cat_Prof"),
                    cat_prof_description=r.get("Catalog_Profile"),
                    catalog=r.get("Catalog"),
                    code_group=r.get("Code_Group"),
                    code_group_description=r.get("Code_Group_Desc"),
                    object_code=r.get("Object_Code"),
                    object_description=r.get("Object_Desc"),
                )
            )

        db.commit()


@router.post("/equipment")
def ingest_equipment(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf_db),
    valid=Depends(utils.token_auth),
):
    """
    RUN ONCE - populate schemas.Equipment
    """
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
                CASE 
                    WHEN "FLOC"."functional_location" LIKE '%-WTRS-%' THEN 'Dewatering'
                    
                    -- [start]
                     WHEN "FLOC"."functional_location" LIKE '%MP-HAUL-%' THEN 'Haul Truck'
                     WHEN "FLOC"."functional_location" LIKE '%MP-EXCV-%' THEN 'Diggers and Drills'
                     WHEN "FLOC"."functional_location" LIKE '%MP-DRLL-%' THEN 'Diggers and Drills'
                     WHEN "FLOC"."functional_location" LIKE '%MP-LOAD-%' THEN 'Ancillary'
                     WHEN "FLOC"."functional_location" LIKE '%MP-DOZR-%' THEN 'Ancillary'
                     WHEN "FLOC"."functional_location" LIKE '%MP-GRDR-%' THEN 'Ancillary'
                    -- [end]

                    ELSE "Department"."Description" 
                END as "department"
                
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

    if result and len(result) > 0:
        crud.equipment.delete_all(db)

        for r in result:
            db.add(
                schemas.Equipment(
                    function_location=pad_floc(r.get("functional_location")),
                    catalog_profile=r.get("catalog_profile"),
                    equipment_description=r.get("equipment_description"),
                    object_type=r.get("object_type"),
                    site=r.get("site"),
                    department=r.get("department"),
                )
            )

        db.commit()


# REDIS
# --------------------------------------------------------------------------------


@router.post("/redis_equipment")
def redis_equipment(
    *,
    db=Depends(utils.get_db),
    valid=Depends(utils.token_auth),
):
    """Site and Department are costly to fetch when constructing results using schemas.Investigation
    - Query redis is faster then using crud for example
    """
    info = db.execute(
        """
        select
            concat(e.function_location, '_', e.equipment_description) as key,
            json_build_object('site',e.site,'department',e.department) as data 
        from "Equipment" e 
    """
    ).fetchall()
    redis_db = redis.get_redis()

    for item in info:
        redis_db.set(item["key"], json.dumps(item["data"]))


@router.post("/redis_email_distribution_list")
def redis_email_distribution_list(
    *,
    csv_file_name: str,
    valid=Depends(utils.token_auth),
):
    """ """
    full_path = f"/app/app/ingest/email_distribution_lists/{csv_file_name}"

    email_lists = {}

    with open(full_path, encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)

        for r in rows:
            site = r["Site"].lower()
            department = r["Department"].lower()
            object_type = r["Object Type"].lower()
            email = r["Email"]

            if site not in email_lists:
                email_lists[site] = {}

            if department not in email_lists[site]:
                email_lists[site][department] = {}

            if object_type not in email_lists[site][department]:
                email_lists[site][department][object_type] = []

            email_lists[site][department][object_type].append(email)

    REDIS_KEY = "email_distribution_list"
    redis_db = redis.get_redis()
    redis_db.set(REDIS_KEY, json.dumps(email_lists))

    return {"message": "success"}


# ------------------
# READ
# ------------------


@router.get("/email_distribution_list")
def email_distribution_list(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    """ """
    redis_db = redis.get_redis()
    return json.loads(redis_db.get("email_distribution_list"))
