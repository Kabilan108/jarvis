from fastapi import FastAPI
from logfire import Logfire

from common.settings import settings


def get_logger(service: str) -> Logfire:
    import logfire

    logger = logfire.configure(
        service_name=service,
        token=settings.LOGFIRE_TOKEN,
        console=logfire.ConsoleOptions(
            min_log_level=settings.LOG_LEVEL,
        ),
    )
    # INFO: monitor how much this costs over time
    logger.instrument_system_metrics()
    return logger


def get_api_logger(fastapi_app: FastAPI) -> Logfire:
    logger = get_logger("api")
    logger.instrument_fastapi(app=fastapi_app, capture_headers=True)
    return logger


bot_logger = get_logger("telegram-bot")
