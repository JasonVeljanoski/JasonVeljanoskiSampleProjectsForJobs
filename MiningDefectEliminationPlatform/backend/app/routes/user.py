from typing import Union
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Body, Depends
from pydantic import StrictBool

from app import config, crud, models, schemas, utils

router = APIRouter()

# ------------------
# READ
# ------------------
if config.DEV_MODE:

    @router.get("/login_dev")
    def local_dev_login(
        *,
        db=Depends(utils.get_db),
    ):
        return utils.create_access_token(utils.get_local_admin(db))


@router.get("/test")
def test(*, db=Depends(utils.get_db)):
    sql = db.query(schemas.Investigation)

    print(sql)


@router.get("/login")
def get_auth_token(
    *,
    db=Depends(utils.get_db),
    code: str,
):
    data = {
        "client_id": config.OAUTH_CLIENT_ID,
        "scope": "openid email",
        "code": code,
        "redirect_uri": config.REDIRECT_URL,
        "grant_type": "authorization_code",
        "client_secret": config.OAUTH_CLIENT_SECRET,
    }

    data = urlencode(data).encode("ascii")
    response = requests.post(config.OAUTH_TOKEN_URL, data)

    if response.status_code >= 400:
        raise utils.errors.CredentialsInvalidException
    response_content = response.json()
    headers = {"Authorization": "Bearer " + response_content["access_token"]}
    user_info = requests.get(config.INFO_URL, headers=headers).json()
    user = crud.user.get_kw_single(db, email=user_info["mail"])

    if not user:
        user_in = schemas.User(email=user_info["mail"], name=user_info["displayName"])
        user = crud.user.create(db, user_in)
    if user.job_title != user_info["jobTitle"]:
        user.job_title = user_info["jobTitle"]

    # User Updates
    user.is_user = True
    user.last_logged_in = utils.get_time_now()
    db.commit()

    # if config.USER_WHITELIST and user.email not in config.USER_WHITELIST:
    #     raise utils.errors.PermissionDeniedException

    return utils.create_access_token(user)


@router.get("", response_model=models.CurrentUser)
def get_user(
    *,
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return user


@router.get("/all", response_model=list[models.User])
def get_users(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.user.all(db)


@router.post("/get_page", response_model=models.PaginationResult[models.User_Full])
def get_user_page(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    page: int,
    count: int,
    sort_by: list[str] = Body(...),
    sort_desc: list[bool] = Body(...),
    filters: models.User_Filters = Body(None),
):
    filters = filters.dict(exclude_unset=True)
    filters["is_user"] = True

    return crud.user.get_page(db, page, count, sort_by, sort_desc, **filters)


# ------------------
# UPDATE
# ------------------
@router.put("/update_permissions", response_model=models.User)
def update_permissions(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_ADMIN,
    update_user: models.User,
):
    return crud.user.update(db, update_user)


@router.patch("/change_team")
def change_team(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    team_id: int,
    team_name: str,
):
    db.query(schemas.User).filter(schemas.User.id == user.id).update(
        {"location_id": team_id, "team_name": team_name, "updated": utils.get_time_now()}
    )
    db.commit()

    # BROADCAST ALERTS
    utils.create_notification(
        db, user.id, f"Team Changed to {team_name}", "Change was updated successfully"
    )


@router.post("/update_users")
def refresh_user(
    *,
    db=Depends(utils.get_db),
    db_sf=Depends(utils.get_sf_db),
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
        has_id = crud.user.get_kw_single(db, sap_number=r["sap_id"])
        has_email = crud.user.get_kw_single(db, email=r["email"])

        # when email match but that row has no sap id
        if has_email and has_id == None:
            has_email.name = r["name"]
            has_email.job_title = r["position"]
            has_email.sap_number = r["sap_id"]
        elif has_id and has_email == None:
            has_id.name = r["name"]
            has_id.job_title = r["position"]
            has_id.email = r["email"]
        elif has_email and has_id:
            if has_email.id == has_id.id:
                has_email.name = r["name"]
                has_email.job_title = r["position"]

            # when the sap id and email in different row in the user table
            else:
                crud.user.delete(db, has_email.id)
                has_id.name = r["name"]
                has_id.job_title = r["position"]
                has_id.email = r["email"]
        else:
            db.add(
                schemas.User(
                    name=r["name"],
                    email=r["email"],
                    job_title=r["position"],
                    sap_number=r["sap_id"],
                )
            )
    db.commit()

    # users = crud.user.all(db)
    # for user in users:
    #     if user.sap_number == None:
    #         crud.user.delete(db, user.id)


@router.post("/watched_groups")
def update_watched_groups(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    watched_groups: models.WatchedGroups,
):
    user.watched_groups = watched_groups.dict()
    db.commit()


# UAT - FEATURE
if not config.PROD_MODE:

    @router.patch("/access")
    def update_access(
        *,
        db=Depends(utils.get_db),
        user: schemas.User = utils.IS_WRITER,
        access: int,
    ):

        db.query(schemas.User).filter(schemas.User.id == user.id).update(
            {
                "access": access,
            }
        )
        db.commit()
