import datetime as dt

import jwt
from fastapi import Depends
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import config, crud, errors, schemas, utils

oauth2_scheme = OAuth2(auto_error=False)

ALGORITHM = "HS256"


def get_current_user(
    *,
    db: Session = Depends(utils.get_db),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    user = None

    try:
        if request and not token:
            token = request.cookies.get("auth._token.social", "")
            token = token[9:] if token else token

        if token:
            if " " in token:
                token = token.split(" ")[1]

            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("user_id")

            user = crud.user.get(db, user_id)

        elif config.DEV_MODE:
            return crud.user.get_local_admin(db)

    except Exception:
        raise errors.CredentialsInvalidException

    if not user:
        raise errors.CredentialsInvalidException

    return user


def create_access_token(user, **extras):
    expires_delta = dt.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = dt.datetime.utcnow() + expires_delta

    data = {"user_id": user.id, "exp": expire, **extras}

    encoded_jwt = jwt.encode(data, config.SECRET_KEY, algorithm=ALGORITHM)

    return dict(
        access_token=encoded_jwt,
        token_type="Bearer",
    )


def token_auth(token: str = None):
    if config.DEV_MODE:
        return True

    # todo: make this better

    if not token or token != config.API_KEY:
        raise errors.CredentialsInvalidException

    return True


# --------------------------------------------------


class PERM_CHECKER:
    def __init__(self, check=None):
        self.check = check

    def __call__(self, user=Depends(get_current_user)):
        if self.check and not self.check(user):
            raise errors.PermissionDeniedException

        return user


IS_LOGGED_IN = Depends(PERM_CHECKER())
IS_WRITER = Depends(PERM_CHECKER(lambda x: x.access >= schemas.Access.WRITER))
IS_ADMIN = Depends(PERM_CHECKER(lambda x: x.access >= schemas.Access.ADMIN))
IS_SUPER_USER = Depends(PERM_CHECKER(lambda x: x.access >= schemas.Access.SUPER))
