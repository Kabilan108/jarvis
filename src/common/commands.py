from telegram import (
    Update,
)
from telegram.ext import ContextTypes

from common.schema import ChatMetadata
from common.logger import bot_logger


def get_metadata(update: Update) -> ChatMetadata:
    if update.effective_sender and update.effective_chat and update.effective_message:
        return ChatMetadata(
            sender=update.effective_sender.id,
            chat_id=update.effective_chat.id,
            message=update.effective_message.text,
        )

    raise Exception("Can not initialize ChatMetadata")


def log_command(command: str, metadata: ChatMetadata, **kwargs) -> None:
    bot_logger.debug(
        "Received {command=} command from {sender=}",
        command=command,
        sender=metadata.sender,
        chat_id=metadata.chat_id,
        **kwargs,
    )


# ---[General Commands]-------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    metadata = get_metadata(update)
    log_command("/start", metadata)
    await context.bot.send_message(
        chat_id=metadata.chat_id,
        text="""\
Hello! I'm JARVIS your personal AI assistant.
""",
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    metadata = get_metadata(update)
    log_command("/help", metadata)
    await context.bot.send_message(
        chat_id=metadata.chat_id,
        text="""\
Available commands:
/start - Start the bot
/help - Show this help message
""",
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    metadata = get_metadata(update)
    log_command("unknown", metadata)
    await context.bot.send_message(
        chat_id=metadata.chat_id,
        text="Sorry, I don't know that command. Use /help to see a list of available commands.",
    )
