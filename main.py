import logging
import json
from telegram import Update 
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.ext import CommandHandler 
from telegram.ext import MessageHandler 
from telegram.ext import filters 

SECRECTS_FILE = ".secret"

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry I can't recognize that, you said '%s'" % update.message.text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry '%s' is not a valid command" % update.message.text)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("[New Request] Got help request")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="help!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("[New Request] Got start request")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def load_secrets():
    with open(SECRECTS_FILE) as f:
        return json.load(f)


def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    secrets = load_secrets()
    application = ApplicationBuilder().token(secrets['bot_token']).build()

    application.add_handler(CommandHandler('start', start)) 
    application.add_handler(CommandHandler('help', help)) 
    # Filters out unknown commands 
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    # Filters out unknown messages. 
    application.add_handler(MessageHandler(filters.TEXT, unknown_text)) 

    application.run_polling() 


if __name__ == '__main__':
    main()