import datetime
import json
import time
from dataclasses import Field

import pytz
from app import crud, models, schemas, utils
from app.utils import redis_helper
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/init_redis_app_settings")
def redis(valid=Depends(utils.token_auth)):
    REDIS_KEY = "app_settings"

    redis_db = redis_helper.Redis_Client()

    redis_db.set(
        REDIS_KEY,
        json.dumps({"uat_email_whitelist": [], "feedback_email_list": []}),
    )


@router.get("/print_redis_store")
def print_redis_store(*, valid=Depends(utils.token_auth)):

    redis_db = redis_helper.Redis_Client()
    redis_all = redis_db.get_all()

    for k, v in redis_all.items():
        print("K - " + k)
        print("  V - " + v)


@router.get("/print_logged_in_users")
def print_logged_in_users(valid=Depends(utils.token_auth)):
    allUser = utils.user.get_logged_in_users_tokens_redis()

    for u in allUser:
        print(
            "User ID: "
            + str(u.userId)
            + " access_token: "
            + u.access_token
            + " refresh_token: "
            + u.refresh_token
            + " timestamp: "
            + str(u.timestamp)
        )

@router.get("/print_number_logged_in_users")
def print_number_logged_in_users(valid=Depends(utils.token_auth)):
    allUser = utils.user.get_logged_in_users_tokens_redis()

    print("Total number logged in Microsoft users: " + str(len(allUser)))
