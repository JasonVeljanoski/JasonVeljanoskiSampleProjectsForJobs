import os

# --------------------------------------------
# Server
# --------------------------------------------

# 60 minutes * 24 hours * 8 days = 8 days
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = f"https://{SERVER_NAME}"
# BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS")  # a string of origins separated by commas
PROJECT_NAME = os.getenv("PROJECT_NAME")
REDIRECT_URL = f"{SERVER_HOST}/auth"


# --------------------------------------------
# Postgres db
# --------------------------------------------

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
)

# --------------------------------------------
# Snowflake db
# --------------------------------------------
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", default="wn74261.ap-southeast-2")
SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB", default="EDW")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", default="SELFSERVICE")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

# --------------------------------------------
# Oath
# --------------------------------------------

OAUTH_TENANT_ID = os.getenv("OAUTH_TENANT_ID")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_SECRET = os.getenv("OAUTH_SECRET")

INFO_URL = "https://graph.microsoft.com/v1.0/me/"
OAUTH_TOKEN_URL = (
    "https://login.microsoftonline.com/143a7396-a856-47d7-8e31-62990b5bacd0/oauth2/v2.0/token"
)

# --------------------------------------------
# Dev or Prod
# --------------------------------------------

DEV_MODE = SERVER_NAME == "localhost"
PROD_MODE = SERVER_NAME == "prod"

if DEV_MODE:
    SECRET_KEY = "00dPSM4wC36q0PFiCJGzSBFdojVTDELZbIzIjIMphUzn2rExm1IIfbgRP8sk20o4"
else:
    SECRET_KEY = os.getenv("SECRET_KEY")

API_KEY = os.getenv("API_KEY")
ENV = os.getenv("ENV", "dev")
