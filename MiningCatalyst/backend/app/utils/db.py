import json

from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config

# --------------------------------------------
# Postgres db
# --------------------------------------------


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


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# --------------------------------------------
# Snowflake db
# --------------------------------------------


SNOWFLAKE_URI = URL(
    account=config.SNOWFLAKE_ACCOUNT,
    database=config.SNOWFLAKE_DB,
    schema=config.SNOWFLAKE_SCHEMA,
    user=config.SNOWFLAKE_USER,
    password=config.SNOWFLAKE_PASSWORD,
)

sf_engine = create_engine(SNOWFLAKE_URI, pool_pre_ping=True, pool_size=30, max_overflow=40)

SessionSnowflake = sessionmaker(bind=sf_engine, autocommit=False, autoflush=True)


def get_sf():
    try:
        db = SessionSnowflake()
        yield db
    finally:
        db.close()
