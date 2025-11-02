from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from snowflake.sqlalchemy import URL

import json

from app import config


def dumps(d):
    return json.dumps(d, default=str)


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=40,
    json_serializer=dumps,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

SNOWFLAKE_URI = URL(
    account="wn74261.ap-southeast-2",
    database="EDW",
    schema="SELFSERVICE",
    user="SVC_RAF",
    password="Eec4beebbac68eac",
)

sf_engine = create_engine(SNOWFLAKE_URI, pool_pre_ping=True, pool_size=30, max_overflow=40)

SessionSnowflake = sessionmaker(bind=sf_engine, autocommit=False, autoflush=True)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_sf():
    try:
        db = SessionSnowflake()
        yield db
    finally:
        db.close()
