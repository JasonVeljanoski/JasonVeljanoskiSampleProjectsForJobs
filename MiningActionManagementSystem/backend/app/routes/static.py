import json
from urllib.parse import urlencode

import requests
from app import config, crud, models, schemas, utils
from app.utils import redis_helper
from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter()

# --------------------------
# READ
# --------------------------
@router.get("/functional_location_permutations")
def get_functional_location_permutations(
    *,
    db=Depends(utils.get_db),
    user=utils.IS_LOGGED_IN
):
    redis_db = redis_helper.Redis_Client()
    res = json.loads(redis_db.get("floc_perms"))
    return res if res else []


@router.get("/full_functional_locations")
def get_full_functional_locations(
    *,
    db=Depends(utils.get_db),
    user=utils.IS_LOGGED_IN
):
    redis_db = redis_helper.Redis_Client()
    res = json.loads(redis_db.get("full_flocs"))
    return res if res else []


@router.get("/workcenters")
def get_workcenters(
    *,
    db=Depends(utils.get_db),
    user=utils.IS_LOGGED_IN
):
    """
    Return list in the form
        Workcenter - Description
    """
    redis_db = redis_helper.Redis_Client()
    res = json.loads(redis_db.get("workcenters"))
    return res if res else []
