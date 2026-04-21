import os
import logging
from urllib.parse import urlencode
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN_BOT")
# APP_LOGIN_URL = os.getenv("APP_LOGIN_URL")
APP_LOGIN_URL = "https://gear-recycler-blend.ngrok-free.dev"

def build_login_url(telegram_id: str, telegram_username: str) -> str:
    query = urlencode(
        {
            "telegram_id": telegram_id,
            "telegram_username": telegram_username or "",
        }
    )
    return f"{APP_LOGIN_URL}/login.html?{query}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)
    telegram_username = update.message.from_user.username
    first_name = update.message.from_user.first_name

    logger.info(f"id={telegram_id}, username={telegram_username}")
    login_url = build_login_url(telegram_id, telegram_username)
    logger.info(f"login_url={login_url}")

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Open Finance Tracker", web_app=WebAppInfo(url=login_url))]],
        resize_keyboard=True,
    )

    user_info_text = (
        "👋 Welcome to Finance Tracker!\n"
        f"{first_name}\n"
        f"Your link for login: {login_url}\n"
    )

    await update.message.reply_text(user_info_text)

    await update.message.reply_text(
        "Tap the button below to login in web app.",
        reply_markup=keyboard,
    )


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
