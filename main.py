import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from bot_commands import *

SECRECTS_FILE = ".secret"


def load_secrets() -> dict:
    with open(SECRECTS_FILE) as f:
        return json.load(f)


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    # Filters out unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    # Filters out unknown messages.
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    secrets = load_secrets()
    application = ApplicationBuilder().token(secrets["bot_token"]).build()
    register_handlers(application)
    application.run_polling()


if __name__ == "__main__":
    main()
