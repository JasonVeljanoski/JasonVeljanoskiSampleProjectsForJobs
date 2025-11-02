import json

from pydantic import BaseModel, Field

from app.utils.redis import get_redis


class SettingsFrontend(BaseModel):
    green_nav_bar: bool = False


class SettingsBackend(BaseModel):
    use_whitelist: bool = False
    user_whitelist: list[str] = []
    admin_list: list[str] = Field(
        default=[
            "jowinter@fmgl.com.au",
            "j.veljanoski@fmgl.com.au",
            "jason.veljanoski@enco.net.au",
            "enco_admin@fmgl.com.au",
        ],
        example=[],
    )


class Settings(SettingsBackend, SettingsFrontend):
    pass


# ------------------------------------------------------------------------------------------------

REDIS_KEY = "app_settings"


def get_settings(model=Settings):
    redis = get_redis()

    if redis.exists(REDIS_KEY):
        return model(**json.loads(redis.get(REDIS_KEY)))

    return model()


def get_frontend_settings() -> SettingsFrontend:
    return get_settings(SettingsFrontend)


def get_backend_settings() -> SettingsBackend:
    return get_settings(SettingsBackend)


def edit_settings(settings: Settings):
    get_redis().set(REDIS_KEY, json.dumps(settings.dict()))

    return settings


def edit_settings_key(key: str, value: str):
    settings = get_settings()

    setattr(settings, key, value)

    return edit_settings(settings)
