import os
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN_BOT")
# ToDo this domain will change all time need connect nginx for https
WEB_APP_URL = "https://cherry-treated-fifth-texas.trycloudflare.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    web_app_button = KeyboardButton(
        text="🔐 Open App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    status_button = KeyboardButton(text="🔍 Check Status")
    
    keyboard = ReplyKeyboardMarkup(
        [[web_app_button], [status_button]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Welcome to Finance Tracker! Press the button below to log in or sign up:",
        reply_markup=keyboard
    )
    logger.info(f"User {update.message.from_user.id} started the bot")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
