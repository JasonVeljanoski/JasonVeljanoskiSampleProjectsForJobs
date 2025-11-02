import csv
import json

from app import crud, models, redis, schemas, utils
from fastapi import APIRouter, Body, Depends, File, UploadFile

router = APIRouter()


# ------------------
# CREATE
# ------------------
@router.post("", response_model=models.General_Attachment)
def upload(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    attachment: UploadFile = File(...),
    metadata: str = Body(...),
):

    metadata = models.General_Attachment_Meta(**json.loads(metadata))

    res = None
    if attachment:
        res = utils.upload_attachments(
            db, schemas.Dashboard_Attachment, None, user, [attachment], [metadata]
        )

    return res[0] if res else None


@router.post("/distribution_list", response_model=models.General_Attachment)
def upload_distribution_list(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    attachment: UploadFile = File(...),
    metadata: str = Body(...),
):

    metadata = models.General_Attachment_Meta(**json.loads(metadata))

    res = None
    if attachment:
        res = utils.upload_attachments(
            db, schemas.Distribution_List_Attachment, None, user, [attachment], [metadata]
        )

    return res[0] if res else None


# ------------------
# READ
# ------------------
@router.get("", response_model=list[models.Dashboard])
def get_dashboard(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN, location_id: int
):
    return crud.dashboard.get_kw(db, location_id=location_id, order_by=schemas.Dashboard.tab_number)


@router.get("/dashboard_attachments", response_model=list[models.General_Attachment])
def get_attachments(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN):
    return crud.general_attachment.get_kw(db, type="Dashboard")


@router.get("/distribution_list_attachments", response_model=list[models.General_Attachment])
def get_distribution_list_attachments(
    *, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN
):
    return crud.general_attachment.get_kw(db, type="Distribution List")


# ------------------
# UPDATE
# ------------------
@router.patch("/selected_distribution_list")
def redis_email_distribution_list(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
    flag: bool,
):

    # 1.  select all the active distribution list attachment
    db.query(schemas.Distribution_List_Attachment).filter(
        schemas.Distribution_List_Attachment.is_active_list.isnot(False)
    ).update({"is_active_list": False})

    # 2.  select the selected attachment so that we can have the path
    attachment = (
        db.query(schemas.General_Attachment).filter(schemas.General_Attachment.id == id).scalar()
    )

    # 3. make the full path of the file here
    full_path = f"{schemas.enums.DocumentPaths.GENERAL.value}/{attachment.unique_filename}"

    # 4. set the is active to be true of false
    db.query(schemas.Distribution_List_Attachment).filter(
        schemas.Distribution_List_Attachment.id == id
    ).update({"is_active_list": flag})

    db.commit()

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
    redis_db.set(REDIS_KEY, json.dumps({}))
    if flag:
        redis_db.set(REDIS_KEY, json.dumps(email_lists))

    return {"message": "success"}


@router.patch("/selected")
def update_selected(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_WRITER,
    id: int,
    flag: bool,
):

    # [1]. Change Flag Status (is_active)

    # reset all to not active
    db.query(schemas.Dashboard_Attachment).filter(
        schemas.Dashboard_Attachment.is_active.isnot(False)
    ).update({"is_active": False})

    # set active
    db.query(schemas.Dashboard_Attachment).filter(schemas.Dashboard_Attachment.id == id).update(
        {"is_active": flag}
    )

    db.commit()

    # ------------------------

    # [2]. Change Dashboard Schema with Updates
    attachment = (
        db.query(schemas.General_Attachment).filter(schemas.General_Attachment.id == id).scalar()
    )

    # meta
    full_path = f"{schemas.enums.DocumentPaths.GENERAL.value}/{attachment.unique_filename}"

    # remove all dashboards
    crud.dashboard.delete_all(db)

    if not flag:
        return

    try:
        # add new dashoards
        with open(full_path, encoding="utf-8-sig") as f:
            rows = csv.DictReader(f)

            for r in rows:

                obj = schemas.Dashboard(
                    title=r["title"],
                    tab_title=r["tab_title"],
                    tab_number=r["tab_number"],
                    tab_type=r["tab_type"],
                    tableau_url=r["tableau_url"],
                    aplus_date_range=r["aplus_date_range"],
                    aplus_site=r["aplus_site"],
                    aplus_area=r["aplus_area"],
                    rems_date_range=r["rems_date_range"],
                    rems_site=r["rems_site"],
                    rems_fleet_type=r["rems_fleet_type"],
                    location_id=int(r["location_id"]),
                    threshold_5_why=int(r["threshold_5_why"] if r["threshold_5_why"] else 2),
                )

                db.add(obj)

                db.commit()
                db.refresh(obj)

                if "aplus_circuits" in r and r["aplus_circuits"]:
                    for circuit in r["aplus_circuits"].split(","):
                        db.add(
                            schemas.Aplus_Circuit_Association(
                                dashboard_id=obj.id,
                                aplus_circuit=circuit.strip(),
                            )
                        )

                db.commit()

    except:
        db.query(schemas.Dashboard_Attachment).filter(schemas.Dashboard_Attachment.id == id).update(
            {"is_active": False}
        )
        db.commit()
        raise Exception("File must be a csv that fits the exact format for a dashboard upload")
