import os

from snowflake.sqlalchemy import URL
from snowflake.sqlalchemy.snowdialect import SnowflakeDialect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config

SnowflakeDialect.supports_statement_cache = False

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_size=30, max_overflow=40
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


SNOWFLAKE_URI = None
sf_engine = None
SFSession = None

# just for the testing purpose
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", default="wn74261.ap-southeast-2")
SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB", default="AA_OPERATIONS_MANAGEMENT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", default="SVC_RAF")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", default="Eec4beebbac68eac")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", default="WH_EDW_SELFSERVICE")


if SNOWFLAKE_USER:
    SNOWFLAKE_URI = URL(
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DB,
        schema="sc",
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        # Snowflake times out after 4hrs of idle
        # Heartbeat thread will keep the session token up to date forever
        CLIENT_SESSION_KEEP_ALIVE="true",
    )

    sf_engine = create_engine(SNOWFLAKE_URI, pool_pre_ping=True, pool_size=10, max_overflow=20)
    SFSession = sessionmaker(bind=sf_engine, autoflush=True, autocommit=False)

# if config.SNOWFLAKE_USER:
#     SNOWFLAKE_URI = URL(
#         account=config.SNOWFLAKE_ACCOUNT,
#         warehouse=config.SNOWFLAKE_WAREHOUSE,
#         database=config.SNOWFLAKE_DB,
#         schema="sc",
#         user=config.SNOWFLAKE_USER,
#         password=config.SNOWFLAKE_PASSWORD,
#     )

#     sf_engine = create_engine(
#         SNOWFLAKE_URI, pool_pre_ping=True, pool_size=30, max_overflow=40)
#     SFSession = sessionmaker(bind=sf_engine, autoflush=True, autocommit=False)


def get_sf_db():
    try:
        db = SFSession()
        yield db
    finally:
        db.close()
