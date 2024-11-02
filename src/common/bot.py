from telegram.ext import ApplicationBuilder
from common.settings import settings

app = ApplicationBuilder().token(settings.BOTFATHER_TOKEN).build()


def get_application():
    return app


def get_bot_instance():
    return app.bot
