import logging
import sys
from telegram.ext import (
    ApplicationBuilder,
    Application,
    filters,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
)
from event_commands import *
from state import *
from event import Events
from disk import flush_data_to_disk, load_data_from_disk, load_secrets


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

    application.add_handler(CommandHandler("show", show_event_stats))
    application.add_handler(
        MessageHandler(filters.Regex(r"^(/show_[\S]+)$"), show_event_stats)
    )


def init_logger():
    file_handler = logging.FileHandler(filename="main_bot.log", mode="a")
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=logging.INFO,
        handlers=handlers,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    init_logger()
    secrets = load_secrets()
    application = ApplicationBuilder().token(secrets["bot_token"]).build()

    application.bot_data["events"] = Events(**load_data_from_disk())

    register_handlers(application)

    try:
        application.run_polling()
    except KeyboardInterrupt:
        logging.info("[Stopped] Bot stopped with KeyboardInterrupt")
    except:
        logging.exception("Unknown excption.")

    flush_data_to_disk(application.bot_data["events"])


if __name__ == "__main__":
    main()
