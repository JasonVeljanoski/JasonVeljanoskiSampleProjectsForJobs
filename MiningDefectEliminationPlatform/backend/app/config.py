import os

# 60 minutes * 24 hours * 8 days = 8 days
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8
SECRET_KEY = os.getenv("SECRET_KEY")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
OAUTH_TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
REDIRECT_URL = os.getenv("REDIRECT_URL")
INFO_URL = os.getenv("INFO_URL")

SERVER_NAME = os.getenv("SERVER_NAME")

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
)

SNOWFLAKE_ACCOUNT = "wn74261.ap-southeast-2"
SNOWFLAKE_DB = "AA_OPERATIONS_MANAGEMENT"
SNOWFLAKE_WAREHOUSE = "WH_EDW_SELFSERVICE"
# SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
# SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

SENTRY_DSN = "" if SERVER_NAME == "localhost" else os.getenv("SENTRY_DSN", "")

DEV_MODE = SERVER_NAME == "localhost"
PROD_MODE = SERVER_NAME == "prod"
API_KEY = os.getenv("API_KEY")
ENV = os.getenv("ENV", "dev")
USER_WHITELIST = None

if ENV != "prod":
    USER_WHITELIST = [  # email white list
        # enco people
        "clinton.smalley@fmgl.com.au",
        "jason.veljanoski@enco.net.au",
        "george.yang@enco.net.au",
        "jowinter@fmgl.com.au",
        "jasonveljanoski@outlook.com",
        # # fmg people
        "rhanning@fmgl.com.au",
        "behislop@fmgl.com.au",
        "campbell.beck@fmgl.com.au",
        "jwhite@fmgl.com.au",
        # "jrow@fmgl.com.au",
    ]
