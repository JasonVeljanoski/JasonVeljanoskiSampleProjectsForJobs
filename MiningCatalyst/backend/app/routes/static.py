from fastapi import APIRouter, Depends
from sqlalchemy import tuple_

from app import crud, models, schemas, utils

router = APIRouter()


@router.post("/ingest_organisational_unit")
def ingest_organisational_unit(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    QUERY_BATCH_SIZE = 1000

    query = """
        SELECT DISTINCT
            "Tier04FullName" as Area,"Tier05FullName" as Department,"Tier06FullName" as Team
        FROM
            EDW.SELFSERVICE."OrganisationalUnit"
    """

    # get the total count of rows to process
    total_rows = db_sf.execute(f"SELECT COUNT(*) FROM ({query})").scalar()

    # sanity
    if not (total_rows and total_rows > 0):
        return {"message": "No new rows to insert"}

    # determine the number of batches
    num_batches = (total_rows // QUERY_BATCH_SIZE) + 1

    # iterate through each batch
    add_counter = 0
    for batch in range(num_batches):
        # calculate the offset and limit for the batch
        offset = batch * QUERY_BATCH_SIZE
        limit = QUERY_BATCH_SIZE

        # build the batch query
        batch_query = f"{query} LIMIT {limit} OFFSET {offset}"

        # get data from snowflake
        items = db_sf.execute(batch_query).mappings().all()

        # remove duplicate rows from snowflake
        data = set()
        seen_pairs = {}
        for item in items:
            area = item.get("area")
            department = item.get("department")
            team = item.get("team")
            pair = (area, department, team)
            if pair not in seen_pairs:
                seen_pairs[pair] = True
                data.add(pair)

        data = list(data)

        # insert data
        existing_data = (
            db.query(schemas.OrganisationalUnit)
            .filter(
                tuple_(
                    schemas.OrganisationalUnit.area,
                    schemas.OrganisationalUnit.department,
                    schemas.OrganisationalUnit.team,
                ).in_(data)
            )
            .all()
        )

        existing_combinations = set([(d.area, d.department, d.team) for d in existing_data])

        data_to_insert = [
            {"area": d[0], "department": d[1], "team": d[2]}
            for d in data
            if ((d[0], d[1], d[2]) not in existing_combinations)
        ]

        if data_to_insert and len(data_to_insert) > 0:
            for d in data_to_insert:
                db.add(
                    schemas.OrganisationalUnit(
                        area=d["area"], department=d["department"], team=d["team"]
                    )
                )
                add_counter += 1

            db.commit()

        # clear the session cache to avoid memory issues
        db.expunge_all()

    return {"message": f"Inserted {add_counter} rows"}


# -------------------------------------------------------------------------


def pad_floc(floc_str):
    FLOC_LENGTHS = [3, 2, 4, 6, 6, 5, 5]  # standard policy for floc length
    keys = floc_str.split("-")

    if len(keys) > 7:
        return None

    padded_floc = []

    for ii in range(len(keys)):
        key = keys[ii]
        floc_len = FLOC_LENGTHS[ii]
        key_len = len(key)

        if key_len < floc_len:
            key += " " * (floc_len - key_len)

        padded_floc.append(key)

    return "-".join(padded_floc)


@router.post("/ingest_equipment")
def ingest_equipment(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    # TODO - this needs to be batched!

    import time

    start = time.time()

    query = """
        DELETE FROM Floc;
        DELETE FROM Equipment;
    """
    db.execute(query)
    db.commit()

    query = """
        select distinct
            "EquipmentDescription" as equipment,
            "FunctionalLocationLabel" as floc
        from AA_ASSETS_MAINTENANCESYSTEMS.QUERY."EquipmentCurrent"
        limit 50
    """
    all = db_sf.execute(query).mappings().all()

    all_equipments = crud.equipment.all(db)

    root_flocs = []

    for a in all:
        floc = a["floc"]

        if floc is None:
            continue

        floc = pad_floc(floc)

        if floc is None:
            continue

        floc_partitions = floc.split("-")

        nodes = []

        for index in range(0, len(floc_partitions)):
            node = "-".join(floc_partitions[0 : index + 1])

            nodes.append(node)

        added = []

        for index, node in enumerate(nodes):
            to_add = schemas.Floc(node=node)

            if index == 0:
                any_matching_roots = [r for r in root_flocs if r.node == node]

                if len(any_matching_roots) > 0:
                    added.append(any_matching_roots[0])
                    continue

            if index > 0:
                prev_node = added[index - 1]

                prev_node.parent = to_add

            db.add(to_add)
            added.append(to_add)

            if index == 0:
                root_flocs.append(to_add)

        equip_description = a["equipment"]

        if equip_description is None:
            continue

        equip_description = equip_description.lower()

        equipment = schemas.Equipment(description=equip_description)

        if equip_description not in [e.description for e in all_equipments]:
            db.add(equipment)
            all_equipments.append(equipment)
        else:
            equipment = [e for e in all_equipments if e.description == equip_description][0]

        added[-1].equipment = equipment

        db.commit()

    end = time.time()

    hours = (end - start) / 3600

    return f"Finished in {hours} hours"


# ------------------------------------------------------------------------------


@router.post("/update_users")
def update_users(
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

    updated_count = 0
    added_count = 0

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
                updated_count += 1
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
                updated_count += 1
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
            added_count += 1

        db.commit()

        return {"message": f"Updated {updated_count} users, added {added_count} users"}


# ------------------------------------------------------------------------------

# * add more here ...


# ------------------------------------------------------------------------------
# Ingest All Static Data
# ------------------------------------------------------------------------------
@router.post("/ingest_all_static_data")
def ingest_all_static_data(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf),
    valid=Depends(utils.token_auth),
):
    ingest_organisational_unit(db=db, db_sf=db_sf, valid=valid)
    ingest_equipment(db=db, db_sf=db_sf, valid=valid)
    update_users(db=db, db_sf=db_sf, valid=valid)


# ------------------------------------------------------------------------------
