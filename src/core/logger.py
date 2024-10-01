from fastapi import FastAPI

from core.settings import settings


def get_logger(service: str):
    import logfire

    logfire.configure(
        service_name=service,
        token=settings.LOGFIRE_TOKEN,
        console=logfire.ConsoleOptions(
            min_log_level=settings.LOG_LEVEL,
        ),
    )
    return logfire


def get_api_logger(fastapi_app: FastAPI):
    logger = get_logger("jarvis-tg-api")
    logger.instrument_fastapi(fastapi_app)
    return logger


bot_logger = get_logger("jarvis-tg-bot")
