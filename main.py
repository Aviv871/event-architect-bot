import logging
import json
from telegram.ext import (
    ApplicationBuilder,
    Application,
    filters,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
)
from event_commands import (
    cancel,
    create_or_join_event,
    handle_event_name,
    handle_item_to_bring_summary,
    handle_more_items_decision,
    handle_more_of_same_item,
    handle_new_item,
    handle_event_creation_summery,
    handle_items_to_bring_selection,
)
from state import *

SECRECTS_FILE = ".secret"


def load_secrets() -> dict:
    with open(SECRECTS_FILE) as f:
        return json.load(f)


def register_handlers(application: Application) -> None:
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", create_or_join_event)],
        states={
            # Event Createion
            ENTERED_NEW_EVENT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_name)
            ],
            ENTERED_NEW_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_item)
            ],
            ENTERED_MORE_OF_SAME_ITEM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_more_of_same_item
                )
            ],
            MORE_ITEMS_DECISION: [CallbackQueryHandler(handle_more_items_decision)],
            EVENT_CREATION_SUMMARY: [
                MessageHandler(filters.ALL, handle_event_creation_summery)
            ],
            # Event Item Regestration
            ENTERED_ITEM_TO_BRING: [
                CallbackQueryHandler(handle_items_to_bring_selection)
            ],
            ITEM_TO_BRING_SUMMARY: [
                MessageHandler(filters.ALL, handle_item_to_bring_summary)
            ],
            # Common
            EMPTY: [MessageHandler(filters.ALL, cancel)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="event_creation_conversion",
        # persistent=True,
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler("start", create_or_join_event))


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    secrets = load_secrets()
    application = ApplicationBuilder().token(secrets["bot_token"]).build()
    register_handlers(application)

    try:
        application.run_polling()
    except Exception:
        logging.info("[Stopped] Bot stopped")


if __name__ == "__main__":
    main()
