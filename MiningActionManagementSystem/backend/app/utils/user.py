import datetime
import json
import urllib
from urllib.parse import urlencode

import requests
from app import config, models, utils
from app.utils import redis_helper

"""
    Given a valid refresh token associated to a user, gets and returns a new access token & refresh token
"""


def get_new_microsoft_tokens(refreshToken):

    data = {
        "client_id": config.OAUTH_CLIENT_ID,
        "scope": "offline_access openid email Group.Read.All GroupMember.Read.All Tasks.ReadWrite User.Read User.ReadBasic.All",
        "refresh_token": refreshToken,
        "grant_type": "refresh_token",
        "client_secret": config.OAUTH_SECRET,
    }

    url = f"https://login.microsoftonline.com/{config.OAUTH_TENANT_ID}/oauth2/v2.0/token"
    data = urlencode(data).encode("ascii")
    response = requests.post(url, data)
    response_content = response.json()

    access_token = response_content["access_token"]
    refresh_token = response_content["refresh_token"]

    return [access_token, refresh_token]


def save_user_tokens_redis(userId, accessToken, refreshToken):

    redis_db = redis_helper.Redis_Client()
    timestamp = utils.get_time_now()

    loggedInUser = models.User_Logged_In(userId, accessToken, refreshToken, timestamp)
    loggedInUserJson = json.dumps(loggedInUser.__dict__, default=str)

    redisKey = "teams_tokens_user_id_" + str(userId)
    redis_db.set(redisKey, loggedInUserJson)


def get_logged_in_users_tokens_redis():

    loggedInUsers = []
    redis_db = redis_helper.Redis_Client()

    redis_all = redis_db.get_all()
    for k, v in redis_all.items():
        if k.startswith("teams_tokens_user_id_"):

            valueObject = json.loads(v)
            loggedInUser = models.User_Logged_In(**valueObject)
            loggedInUsers.append(loggedInUser)

    return loggedInUsers
