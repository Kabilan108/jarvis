from telegram.ext import ApplicationBuilder
from core.settings import settings

app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()


def get_application():
    return app


def get_bot_instance():
    return app.bot
