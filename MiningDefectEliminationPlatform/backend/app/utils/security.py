import datetime as dt

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2
from sqlalchemy.orm import Session

from .db import get_db
from .errors import CredentialsInvalidException

oauth2_scheme = OAuth2(auto_error=False)
ALGORITHM = "HS256"


def get_current_user(
    *,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    from app import config, crud

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
            return get_local_admin(db)

    except Exception:
        raise CredentialsInvalidException

    if not user:
        raise CredentialsInvalidException

    return user


def create_access_token(user):
    from app import config

    expires_delta = dt.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = dt.datetime.utcnow() + expires_delta

    data = {"user_id": user.id, "exp": expire}

    encoded_jwt = jwt.encode(data, config.SECRET_KEY, algorithm=ALGORITHM)
    return dict(
        access_token=encoded_jwt,
        token_type="Bearer",
    )


def get_local_admin(db):
    from app import crud, schemas

    email = "dev@enco.net.au"
    user = crud.user.get_kw_single(db, email=email)
    if not user:
        user_in = schemas.User(
            email=email,
            name="Enco",
            access=schemas.Access.ADMIN,
        )
        user = crud.user.create(db, user_in)

    return user


def token_auth(token: str = None):
    from app import config

    if config.DEV_MODE:
        return True

    # TODO make this better

    if not token or token != config.API_KEY:
        raise CredentialsInvalidException

    return True


class Perm_Checker:
    def __init__(self, checker=None) -> None:
        self.checker = checker

    def __call__(self, user=Depends(get_current_user)):
        if self.checker and not self.checker(user):
            raise CredentialsInvalidException

        return user


IS_LOGGED_IN = Depends(Perm_Checker())
IS_WRITER = Depends(Perm_Checker(lambda x: x.is_writer))
IS_ADMIN = Depends(Perm_Checker(lambda x: x.is_admin))
