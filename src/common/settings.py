from pydantic_settings import BaseSettings, SettingsConfigDict
from logfire import LevelName
import pydantic


class Settings(BaseSettings):
    NAME: str = "jarvis"
    VERSION: str = "0.0.1"

    API_KEY: str
    LOG_LEVEL: LevelName
    LOGFIRE_TOKEN: str
    BOTFATHER_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    try:
        return Settings()
    except pydantic.ValidationError as e:
        print(f"Settings validation error: {e}")
        raise


settings = get_settings()
