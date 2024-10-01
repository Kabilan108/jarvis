from telegram.ext import CommandHandler, filters, MessageHandler

from time import strftime

from core.commands import (
    help,
    start,
    unknown,
)
from core.logger import bot_logger
from core.bot import get_application


def main():
    app = get_application()

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)

    help_handler = CommandHandler("help", help)
    app.add_handler(help_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(unknown_handler)

    with bot_logger.span(
        f"JARVIS Telegram Bot Instance Running from: {strftime('%Y.%m.%d - %H:%M:%S')}"
    ):
        app.run_polling()
        bot_logger.info(f"bot stopped at {strftime('%Y%m%d_%H:%M:%S')}")


if __name__ == "__main__":
    main()
