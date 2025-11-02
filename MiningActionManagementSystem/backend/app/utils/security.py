import datetime as dt

import jwt
from app import config, crud, schemas, utils
from app.schemas.enums import PrivacyEnum
from fastapi import Depends
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from starlette.requests import Request

from . import errors

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

    # TODO make this better

    if not token or token != config.API_KEY:
        raise errors.CredentialsInvalidException

    return True


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


####################################################################################
####### ACCESS CONTROL METHODS - READ & EDIT ACTIONS & WORKGROUPS #######


"""
Workgroup_CanRead   - Determines if a User has permission to Read the Workgroup
Returns True if:
    1) Workgroup privacy is PUBLIC, OR
    2) User is Admin of Workgroup, OR User is Assigned to Workgroup (Owner), OR User is Member of Workgroup
"""


def Workgroup_CanRead(db, userId, workgroupId):
    workgroup = crud.workgroup.get(db, workgroupId)

    # 1)
    if workgroup.privacy == PrivacyEnum.PUBLIC:
        return True

    # 2)
    if (
        userId in workgroup.admin_ids
        or workgroup.owner_id == userId
        or userId in workgroup.member_ids
    ):
        return True

    # Criteria not matched, does not have permission
    return False


"""
Workgroup_CanEdit   - Determines if a User has permission to Edit the Workgroup
Returns True if:
    1) User is Admin of Workgroup, OR User is Assigned to Workgroup (Owner)
"""


def Workgroup_CanEdit(db, userId, workgroupId):
    workgroup = crud.workgroup.get(db, workgroupId)

    # 1)
    if userId in workgroup.admin_ids or workgroup.owner_id == userId:
        return True

    # Criteria not matched, does not have permission
    return False


"""
Action_CanRead  - Determines if a User has permission to Read the Action
Returns True if:
    1) Action privacy is PUBLIC, OR
    2) User is Supervisor of Action, OR User is Assigned to Action (Owner), OR User is Member of Action
    3) User has permission to Read the Workgroup that the Action is associated to

    **NOTE: If this method is called with workgroupId==-1, and it gets to 3), it will get the workgroup IDs that the action
            is associated to automatically, and check those, instead of having supplied it.
            This is to make calling this method from other methods/routes easier
"""


def Action_CanRead(db, userId, actionId, workgroupId):
    action = crud.action.get(db, actionId)

    # 1)
    if action.privacy == PrivacyEnum.PUBLIC:
        return True

    # 2)
    if action.supervisor_id == userId or action.owner_id == userId or userId in action.member_ids:
        return True

    # 3)
    if workgroupId == -1:
        # Get the workgroup ID(s) that this action belongs to, and check each one
        workgroup_assocs_query = (
            db.query(schemas.Workgroup_Action_Association.workgroup_id)
            .where(schemas.Workgroup_Action_Association.action_id == actionId)
            .distinct()
        )
        workgroup_assocs_workgroup_ids = db.scalars(workgroup_assocs_query).all()

        # Check permissions for each workgroup
        for workgroup_id in workgroup_assocs_workgroup_ids:
            if Workgroup_CanRead(db, userId, workgroup_id) == True:
                return True
        # If above didn't return true, permissions denied
        return False
    else:
        return Workgroup_CanRead(db, userId, workgroupId)


"""
Action_CanEdit  - Determines if a User has permission to Edit the Action
Returns True if:
    1) User has permission to Read the Action
"""


def Action_CanEdit(db, userId, actionId, workgroupId):
    return Action_CanRead(db, userId, actionId, workgroupId)
