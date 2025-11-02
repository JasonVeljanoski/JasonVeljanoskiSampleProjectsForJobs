import datetime as dt
import json
import os
from typing import List
from urllib.parse import urlencode

import requests
from app import config, crud, models, schemas, utils
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from starlette.responses import FileResponse

router = APIRouter()


# --------------------- #
#  GETTERS
# --------------------- #

# --------------------- #
#  POSTERS
# --------------------- #
