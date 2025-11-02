import json

from pydantic import BaseModel, Field

from app.utils import redis_helper


class Settings_Frontend(BaseModel):
    pass


class Settings_Backend(BaseModel):
    uat_email_whitelist: list[str] = []
    feedback_email_list: list[str] = []


class Settings(Settings_Backend, Settings_Frontend):
    pass


# ------------------------------------------------------------------------------------------------

REDIS_KEY = "app_settings"


def get_settings(model=Settings):
    redis = redis_helper.Redis_Client()

    if redis.exists(REDIS_KEY):
        return model(**json.loads(redis.get(REDIS_KEY)))

    return model()


def get_frontend_settings() -> Settings_Frontend:
    return get_settings(Settings_Frontend)


def get_backend_settings() -> Settings_Backend:
    return get_settings(Settings_Backend)


def edit_settings(settings: Settings):
    redis_helper.Redis_Client().set(REDIS_KEY, json.dumps(settings.dict()))

    return settings


def edit_settings_key(key: str, value: str):
    settings = get_settings()

    setattr(settings, key, value)

    return edit_settings(settings)
