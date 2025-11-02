from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Body, Depends
from sqlalchemy import func, or_

from app import config, crud, models, schemas, utils

router = APIRouter()


# ------------------
# CREATE
# ------------------


# ------------------
# READ
# ------------------
@router.get("/login")
def get_auth_token(
    *,
    db=Depends(utils.get_db),
    code: str,
):
    data = {
        "client_id": config.OAUTH_CLIENT_ID,
        "scope": "offline_access openid email",
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

    if not user:
        user_in = schemas.User(email=user_info["mail"], name=user_info["displayName"])
        user = crud.user.create(db, user_in)
    if user.job_title != user_info["jobTitle"]:
        user.job_title = user_info["jobTitle"]

    # User Updates
    user.is_user = True
    user.last_logged_in = utils.get_time_now()
    db.commit()

    return utils.create_access_token(user)


if config.DEV_MODE:

    @router.get("/backdoor")
    def local_backdoor(
        *,
        db=Depends(utils.get_db),
    ):
        return utils.create_access_token(crud.user.get_local_admin(db))


@router.get("", response_model=models.User)
def get_user(*, db=Depends(utils.get_db), user: schemas.User = utils.IS_LOGGED_IN):
    user.last_logged_in = utils.get_time_now()
    user.is_user = True
    db.commit()
    return user


@router.get("/HALP", response_model=models.User)
def get_user2(*, db=Depends(utils.get_db), id: int):
    import time

    time.sleep(3)

    return {"id": id, "name": "test"}


@router.get("/supervisor", response_model=models.UserBasic)
def get_users_supervisor(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    user_id: int = None,
):
    res = crud.user.get(db, user_id)

    if res.supervisor_id is None:
        raise utils.errors.NotFoundException(message="Cannot find users supervisor")

    return crud.user.get(db, res.supervisor_id)


@router.get("/all", response_model=list[models.UserBasic])
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
            # schemas.User.job_title,
            schemas.User.last_logged_in,
            schemas.User.access,
        )
        .filter(schemas.User.is_user)
        .order_by(schemas.User.name)
        .all()
    )


@router.get("/search/user", response_model=list[models.User])
def search_users(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    search: str = None,
):
    if len(search) < 2:
        return []

    search = search.lower()

    return (
        db.query(schemas.User)
        .filter(
            or_(
                func.lower(schemas.User.name).ilike(f"%{search}%"),
                func.lower(schemas.User.email).ilike(f"%{search}%"),
            )
        )
        .all()
    )


@router.post("/users", response_model=list[models.User])
def get_users_from_ids(
    *,
    db=Depends(utils.get_db),
    user: schemas.User = utils.IS_LOGGED_IN,
    ids: list[int] = Body(...),
):
    return crud.user.get_all(db, ids)


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


if not config.PROD_MODE:

    @router.put("/access")
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
