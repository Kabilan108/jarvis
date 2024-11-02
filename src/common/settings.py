from pydantic_settings import BaseSettings, SettingsConfigDict
from logfire import LevelName
import pydantic


class Settings(BaseSettings):
    API_KEY: str = "api-key"
    LOG_LEVEL: LevelName = "info"
    LOGFIRE_TOKEN: str
    MONGODB_NAME: str = ""
    MONGODB_URI: str = ""
    BOTFATHER_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    try:
        return Settings()
    except pydantic.ValidationError as e:
        print(f"Settings validation error: {e}")
        raise


settings = get_settings()
