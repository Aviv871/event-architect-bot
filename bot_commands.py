import logging
from telegram import Update
from telegram.ext import ContextTypes


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry I can't recognize that, you said '%s'" % update.message.text,
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry '%s' is not a valid command" % update.message.text,
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("[New Request] Got help request")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="help!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("[New Request] Got start request")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )
