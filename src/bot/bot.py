import os
import logging
import httpx
from io import BytesIO
from urllib.parse import urlencode
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN_BOT")
APP_URL = os.getenv("APP_URL")

def build_login_url(telegram_id: str, telegram_username: str) -> str:
    query = urlencode(
        {
            "telegram_id": telegram_id,
            "webapp_rev": "2026-04-21-1",
        }
    )
    return f"{APP_URL}/login.html?{query}"


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

async def every_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info(f"Received message: {text}")

    await update.message.reply_text(f"You wrote: {text}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]
    tg_file = await photo.get_file()

    buffer = BytesIO()
    await tg_file.download_to_memory(out=buffer)
    buffer.seek(0)

    telegram_id = str(update.effective_user.id)

    files = {
        "file": ("receipt.jpg", buffer, "image/jpeg")
    }

    data = {
        "telegram_id": telegram_id,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{APP_URL}/records/save-record-photo",
            files=files,
            data=data,
            timeout=30
        )

    if response.status_code == 200:
        await update.message.reply_text("✅ Photo uploaded successfully! Receipt is being processed.")
    else:
        await update.message.reply_text("Failed to process photo")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, every_message))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

if __name__ == "__main__":
    app.run_polling()
