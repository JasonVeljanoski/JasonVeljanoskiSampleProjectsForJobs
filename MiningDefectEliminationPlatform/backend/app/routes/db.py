import os
import re
import subprocess
import traceback
from tkinter import E

import sqlalchemy as sql
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from app import config, schemas, utils
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

router = APIRouter()


@router.post("/terminate")
def terminate_pgsql_sessions(*, db=Depends(utils.get_db)):
    query = """
        SELECT
            pg_terminate_backend(pid)
        FROM
            pg_stat_activity
        WHERE
            "backend_start" < current_date - integer '3'
            AND "state" != 'active'
            AND "application_name" LIKE 'pgAdmin%'
    """
    results = db.execute(query).mappings().all()
    return f"Terminated {len(results)} sessions."
