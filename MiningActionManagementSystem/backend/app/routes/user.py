import asyncio
import csv
from urllib import response
from urllib.parse import urlencode

import requests
from app import config, crud, email, models, routes, schemas, utils
from fastapi import APIRouter, BackgroundTasks, Body, Depends

router = APIRouter()

# ------------------
# CREATE
# ------------------

# ------------------
# READ
# ------------------
@router.get("/login")
async def get_auth_token(
    *,
    db=Depends(utils.get_db),
    code: str,
    background_task: BackgroundTasks = None,
):
    # Scope -- Permissions -- Group.Read.All, GroupMember.Read.All Task.ReadWrite User.Read -- Given access 01/02/2023 -- Teams Tasks

    data = {
        "client_id": config.OAUTH_CLIENT_ID,
        "scope": "offline_access openid email Group.Read.All GroupMember.Read.All Tasks.ReadWrite User.Read User.ReadBasic.All",
        # "scope": "offline_access openid email",
        "code": code,
        "redirect_uri": config.REDIRECT_URL,
        "grant_type": "authorization_code",
        "client_secret": config.OAUTH_SECRET,
    }

    data = urlencode(data).encode("ascii")
    response = requests.post(config.OAUTH_TOKEN_URL, data)

    if response.status_code >= 400:
        raise utils.errors.CredentialsInvalidException
    response_content = response.json()

    headers = {"Authorization": "Bearer " + response_content["access_token"]}
    user_info = requests.get(config.INFO_URL, headers=headers).json()
    user = crud.user.get_kw_single(db, email=user_info["mail"])
    microsoft_id_str = user_info["id"]

    if not user:
        user_in = schemas.User(
            email=user_info["mail"], name=user_info["displayName"], microsoft_id=microsoft_id_str
        )
        user = crud.user.create(db, user_in)
    if user.job_title != user_info["jobTitle"]:
        user.job_title = user_info["jobTitle"]
    if user.microsoft_id == None or user.microsoft_id == "":
        user.microsoft_id = microsoft_id_str

    # Save Users Tokens in Redis
    access_token_ = response_content["access_token"]
    refresh_token = response_content["refresh_token"]
    utils.user.save_user_tokens_redis(user.id, access_token_, refresh_token)

    # User Updates
    user.is_user = True
    user.last_logged_in = utils.get_time_now()
    db.commit()

    # if config.USER_WHITELIST and user.email not in config.USER_WHITELIST:
    #     raise utils.errors.PermissionDeniedException

    # Create Log - Login
    crud.log.create_login_log(db, user.id)

    return utils.create_access_token(user)


if config.DEV_MODE:

    @router.get("/backdoor")
    async def local_backdoor(
        *,
        db=Depends(utils.get_db),
        background_task: BackgroundTasks = None,
    ):

        # Create Log - Login
        crud.log.create_login_log(db, crud.user.get_local_admin(db).id)
        return utils.create_access_token(crud.user.get_local_admin(db))


@router.get("", response_model=models.User)
def get_user(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN):
    user.last_logged_in = utils.get_time_now()
    db.commit()
    return user


@router.get("/all", response_model=list[models.User_Basic])
def get_all_users(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
):
    return crud.user.all(db)


@router.get("/all/basic")
def get_all_basic(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_ADMIN,
):

    return (
        db.query(
            schemas.User.id,
            schemas.User.name,
            schemas.User.email,
            schemas.User.job_title,
            schemas.User.last_logged_in,
            schemas.User.access,
        )
        .filter(schemas.User.is_user)
        .order_by(schemas.User.name)
        .all()
    )


"""
@router.get("/impersonate")
def impersonate_user(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_SUPER_USER,
    id: int,
):
    return utils.create_access_token(crud.user.get(db, id), is_impersonating=True)
"""

# ------------------
# UPDATE
# ------------------
@router.put("")
def update_user(
    *,
    db=Depends(utils.get_db),
    edits: models.User,
    user: schemas.User = utils.IS_WRITER,
):
    edit_user = crud.user.get(db, edits.id)
    my_access = user.access

    if edits.access is not None:
        # Cant give someone more access than you have
        if edits.access > my_access:
            raise utils.errors.CredentialsInvalidException

        # Cant modify someones access if they have more than you
        if edit_user.access > my_access:
            raise utils.errors.CredentialsInvalidException
    # else:
    #     del edits.access

    # otherwise
    return crud.user.update(db, edits)


# ------------------
# FOR TESTING ONLY - remove later
# ONLY IN UAT - METHOD USED FOR BASIC <-> ADMIN <-> SUPER ADMIN Navbar
# ------------------
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


# TODO - Remove Route + ingest/employees.csv after running this on prod
@router.get("/ingest_ids")
def ingest_ids_csv(*, db=Depends(utils.get_db), valid=Depends(utils.token_auth)):

    employees_csv_path = "/app/app/ingest/employees.csv"

    class Fmg_User:
        displayName: str = None
        jobTitle: str = None
        mail: str = None
        id: str = None

        def __init__(self, id, name, email, job):
            self.id = id
            self.displayName = name
            self.mail = email
            self.jobTitle = job

    fmg_users = []

    i = 0
    with open(employees_csv_path) as stream:
        reader = csv.reader(stream)
        for row in reader:
            if i == 0:
                i = i + 1
                continue
            fmg_user = Fmg_User(*row)
            fmg_users.append(fmg_user)

    print("CSV parsed into objects list")

    for fmg_user in fmg_users:
        user = crud.user.get_kw_single(db, email=fmg_user.mail)
        if user != None:
            user.microsoft_id = fmg_user.id
            db.commit()
