import logging
import json
from telegram.ext import (
    ApplicationBuilder,
    Application,
    filters,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler
)
from bot_commands import *
from state import *

SECRECTS_FILE = ".secret"


def load_secrets() -> dict:
    with open(SECRECTS_FILE) as f:
        return json.load(f)


def register_handlers(application: Application) -> None:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CAR_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, car_type)
            ],
            CAR_COLOR: [CallbackQueryHandler(car_color)],
            CAR_MILEAGE_DECISION: [
                CallbackQueryHandler(car_mileage_decision)
            ],
            CAR_MILEAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, car_mileage)
            ],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler("skip", skip_photo),
            ],
            SUMMARY: [MessageHandler(filters.ALL, summary)],
            EMPTY: [MessageHandler(filters.ALL, cancel)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler("start", start))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=logging.INFO,
    )

    secrets = load_secrets()
    application = ApplicationBuilder().token(secrets["bot_token"]).build()
    register_handlers(application)

    try:
        application.run_polling()
    except Exception:
        logging.info("[Stopped] Bot stopped")


if __name__ == "__main__":
    main()
