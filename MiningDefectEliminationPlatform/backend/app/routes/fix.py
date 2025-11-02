import csv
import os

from fastapi import APIRouter, Depends
from pydantic import parse_obj_as
from sqlalchemy import and_

from app import crud, models, schemas, utils
from app.schemas.enums import PriorityEnum, StatusEnum

router = APIRouter()


@router.post("/fix_has_completed_rca")
def fix_has_completed_rca(
    db=Depends(utils.get_db),
):
    """ """
    # get all investigations
    res = db.query(schemas.Investigation).all()

    count = 0
    for item in res:
        if item.root_cause_detail is None:
            continue

        _path = (
            f"{schemas.enums.DocumentPaths.RCA.value}/{item.root_cause_detail.complete_rca_fname}"
        )

        if _path and os.path.exists(_path):
            print(f"Found {item.title} {item.id}")
            item.has_completed_rca = True
            db.query(schemas.Investigation).filter(schemas.Investigation.id == item.id).update(
                {
                    "has_completed_rca": True,
                }
            )
            db.commit()
            count += 1

    return f"Successfully updated {count} has_completed_rca values."


@router.post("/fix_investigation_causes")
async def fix_investigation_causes(
    db=Depends(utils.get_db),
):
    """
    Root cause details contain a cause column which should be consistant with the cause column in the investigation table.
    Ingesting historical data has caused this to be inconsistent.

    Investigations : 1553/1597 have no cause
    Root Cause Details: 1553/1597 have no cause
    """
    res = (
        db.query(schemas.Investigation)
        .join(schemas.Root_Cause_Detail)
        .filter(
            and_(
                schemas.Investigation.cause_code == None,
                schemas.Root_Cause_Detail.cause_code != None,
            )
        )
        .all()
    )

    count = 0
    for item in res:
        message = f"(Change) {item.title} ====> {item.root_cause_detail.cause_code}"
        print(message)

        item.cause_code = item.root_cause_detail.cause_code

        db.query(schemas.Investigation).filter(schemas.Investigation.id == item.id).update(
            {
                "cause_code": item.root_cause_detail.cause_code,
            }
        )
        db.commit()

        count += 1

    res = (
        db.query(schemas.Investigation)
        .join(schemas.Root_Cause_Detail)
        .filter(
            and_(
                schemas.Investigation.cause_code == None,
                schemas.Root_Cause_Detail.cause_code != None,
            )
        )
        .all()
    )

    return f"Successfully fixed {count} investigation causes. {len(res)} bad values remaining."


@router.post("/fix_none_five_why_is_complete")
def fix_none_five_why_is_complete(
    db=Depends(utils.get_db),
):
    """
    Five Why is_complete column is set to None when it should be False
    """
    res = db.query(schemas.Five_Why).filter(schemas.Five_Why.is_complete == None).all()

    count = 0
    for item in res:
        message = f"(Change) {item.event_description} ====> {item.is_complete}"
        print(message)

        item.is_complete = False

        db.query(schemas.Five_Why).filter(schemas.Five_Why.id == item.id).update(
            {
                "is_complete": False,
            }
        )
        db.commit()

        count += 1

    res = db.query(schemas.Five_Why).filter(schemas.Five_Why.is_complete == None).all()

    return (
        f"Successfully fixed {count} five_why is_complete values. {len(res)} bad values remaining."
    )


# @router.get("/fix_preffered_names_in_users_table")
# def fix_preffered_names_in_users_table(
#     *,
#     db=Depends(utils.get_db),
#     db_sf=Depends(utils.get_sf_db),
#     user: schemas.User = utils.IS_ADMIN,
# ):
#     query = """
#         SELECT
#             CONCAT(
#                 COALESCE("PreferredName","FirstName"),
#                 ' ',
#                 INITCAP("LastName")
#             ) as "name",
#             LOWER("Email") as "email",
#             "JobTitle" as "position",
#             "Employee_BK" as "sap_id",
#             "Key_Employee_Supervisor" as "supervisor_sap_id"
#         FROM "EDW"."SELFSERVICE"."Employee"
#         WHERE "TerminationDate" > CURRENT_TIMESTAMP
#             AND "Email" IS NOT NULL
#             AND "PositionStatus" = 'Current'
#     """
#     results = db_sf.execute(query).mappings().all()
#     results = parse_obj_as(list[models.User], results)

#     for r in results:
#         user = crud.user.get_kw(db, email=r.email)
#         if user and "name" in user and "name" in r and user.name != r.name:
#             print(f"Updating {user.name} to {r.name}")
#             user.name = r.name
#             db.commit()


@router.get("/reupload_dashboard")
def reupload_dashboard(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_ADMIN,
    csv_file_name: str = None,
):
    # meta
    full_path = f"/app/app/ingest/dashboards/{csv_file_name}"

    # remove all dashboards
    crud.dashboard.delete_all(db)

    # add new dashoards
    with open(full_path, encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)

        for r in rows:

            db.add(
                schemas.Dashboard(
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
            )

        db.commit()


# Code below this point was only used to fix the data in the database
# -----------------------------------------------------------


# @router.get("/restore_historical_actions")
# def restore_historical_actions(
#     *,
#     db=Depends(utils.get_db),
#     user: schemas.User = utils.IS_ADMIN,
# ):
#     class Action(models.Base):
#         id: int = None
#         created: datetime = None
#         updated: datetime = None
#         date_due: datetime = None
#         date_closed: datetime = None
#         archive_datetime: datetime = None
#         investigation_id: int = None
#         five_why_id: int = None
#         flash_report_id: int = None
#         root_cause_detail_id: int = None
#         title: str = None
#         description: str = None
#         status: StatusEnum = None
#         priority: PriorityEnum = None
#         is_historical: int = None
#         supervisor_id: int = None
#         is_archived: bool = None
#         archive_user_id: int = None

#     csv_file_name = "action.csv"
#     full_path = f"/app/app/ingest/dump_2022_10_27/{csv_file_name}"
#     counter = 0

#     with open(full_path, encoding="utf-8-sig") as f:
#         rows = csv.DictReader(f)

#         def HandleNull(x):
#             if x == "\\N":
#                 return None
#             else:
#                 return x

#         def X(x):
#             x = HandleNull(x)
#             if x:
#                 x = x.split(".")[0]
#                 x = x.split("+")[0]
#                 return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

#         for r in rows:

#             # Null hanlde
#             for x in r:
#                 r[x] = HandleNull(r[x])

#             # Historical
#             if r["is_historical"] == "0":
#                 continue

#             # Dates
#             r["created"] = X(r["created"])
#             r["updated"] = X(r["updated"])
#             r["date_due"] = X(r["date_due"])
#             r["archive_datetime"] = X(r["archive_datetime"])

#             if r["status"] == "1" and r["date_closed"] == "2022-08-01 08:00:00.000 +0800":
#                 r["date_closed"] = None
#             else:
#                 r["date_closed"] = X(r["date_closed"])

#             # Forein Keys
#             r["five_why_id"] = int(r["five_why_id"]) if r["five_why_id"] else None
#             r["flash_report_id"] = int(r["flash_report_id"]) if r["flash_report_id"] else None
#             r["root_cause_detail_id"] = (
#                 int(r["root_cause_detail_id"]) if r["root_cause_detail_id"] else None
#             )
#             r["supervisor_id"] = int(r["supervisor_id"]) if r["supervisor_id"] else None
#             r["archive_user_id"] = int(r["archive_user_id"]) if r["archive_user_id"] else None

#             r = parse_obj_as(Action, r)

#             db.merge(
#                 schemas.Action(
#                     id=r.id,
#                     created=r.created,
#                     updated=r.updated,
#                     date_due=r.date_due,
#                     date_closed=r.date_closed,
#                     archive_datetime=r.archive_datetime,
#                     investigation_id=r.investigation_id,
#                     five_why_id=r.five_why_id,
#                     flash_report_id=r.flash_report_id,
#                     root_cause_detail_id=r.root_cause_detail_id,
#                     title=r.title,
#                     description=r.description,
#                     status=r.status,
#                     priority=r.priority,
#                     is_historical=r.is_historical,
#                     supervisor_id=r.supervisor_id,
#                     is_archived=r.is_archived,
#                     archive_user_id=r.archive_user_id,
#                 )
#             )

#             counter += 1

#         db.commit()

#         print(f"\n\n\n==> added {counter} actions\n\n\n")


# @router.get("/restore_historical_action_comments")
# def restore_historical_action_comments(
#     *,
#     db=Depends(utils.get_db),
#     user: schemas.User = utils.IS_ADMIN,
# ):
#     class Action_Comment(models.Base):
#         created: datetime = None
#         updated: datetime = None
#         action_id: int = None
#         user_id: int = None
#         comment: str = None

#     csv_file_name = "action_comment.csv"
#     full_path = f"/app/app/ingest/dump_2022_10_27/{csv_file_name}"
#     counter = 0

#     with open(full_path, encoding="utf-8-sig") as f:
#         rows = csv.DictReader(f)

#         def HandleNull(x):
#             if x == "\\N":
#                 return None
#             else:
#                 return x

#         def X(x):
#             x = HandleNull(x)
#             if x:
#                 x = x.split(".")[0]
#                 x = x.split("+")[0]
#                 return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

#         for r in rows:

#             # Null hanlde
#             for x in r:
#                 r[x] = HandleNull(r[x])

#             # Dates
#             r["created"] = X(r["created"])
#             r["updated"] = X(r["updated"])

#             # Forein Keys
#             r["action_id"] = int(r["action_id"]) if r["action_id"] else None
#             r["user_id"] = int(r["user_id"]) if r["user_id"] else None

#             r = parse_obj_as(Action_Comment, r)

#             db.merge(
#                 schemas.Action_Comment(
#                     created=r.created,
#                     updated=r.updated,
#                     action_id=r.action_id,
#                     user_id=r.user_id,
#                     comment=r.comment,
#                 )
#             )

#             counter += 1

#         db.commit()

#         print(f"\n\n\n==> added {counter} actions\n\n\n")


# @router.get("/restore_historical_action_owner_association")
# def restore_historical_action_owner_association(
#     *,
#     db=Depends(utils.get_db),
#     user: schemas.User = utils.IS_ADMIN,
# ):
#     class Action_Owner_Association(models.Base):
#         created: datetime = None
#         updated: datetime = None
#         action_id: int = None
#         user_id: int = None

#     csv_file_name = "aoa.csv"
#     full_path = f"/app/app/ingest/dump_2022_10_27/{csv_file_name}"
#     counter = 0

#     with open(full_path, encoding="utf-8-sig") as f:
#         rows = csv.DictReader(f)

#         def HandleNull(x):
#             if x == "\\N":
#                 return None
#             else:
#                 return x

#         def X(x):
#             x = HandleNull(x)
#             if x:
#                 x = x.split(".")[0]
#                 x = x.split("+")[0]
#                 return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

#         for r in rows:

#             # Null hanlde
#             for x in r:
#                 r[x] = HandleNull(r[x])

#             # Dates
#             r["created"] = X(r["created"])
#             r["updated"] = X(r["updated"])

#             # Forein Keys
#             r["action_id"] = int(r["action_id"]) if r["action_id"] else None
#             r["user_id"] = int(r["user_id"]) if r["user_id"] else None

#             r = parse_obj_as(Action_Owner_Association, r)

#             db.merge(
#                 schemas.Action_Owner_Association(
#                     created=r.created,
#                     updated=r.updated,
#                     action_id=r.action_id,
#                     user_id=r.user_id,
#                 )
#             )

#             counter += 1

#         db.commit()

#         print(f"\n\n\n==> added {counter} actions\n\n\n")

# Code below this point was only used to make only max of 2 owners for an investigation
# --------------------------------------------------------------------------------------


# @router.post("/trim_owners")
# def trim_owners(
#     *,
#     db=Depends(utils.get_db),
#     user: schemas.User = utils.IS_ADMIN,
# ):
#     action_ids = db.query(schemas.Action.id)
#     action_ids = [x[0] for x in action_ids]

#     for action_id in action_ids:
#         owners = db.query(schemas.Action_Owner_Association).filter_by(action_id=action_id).all()
#         if len(owners) > 2:
#             for owner in owners[2:]:
#                 db.delete(owner)
#                 db.commit()
#                 print(f"deleted {owner}")
#         else:
#             print(f"no need to delete {owners}")
