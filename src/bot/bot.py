import os
import uuid
import logging
from src.models.user import User
from src.services.auth_service import AuthService
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from src.db.database import SessionLocal
from src.repositories.user import UserRepository
from src.repositories.record import RecordRepository
from src.services.record import RecordService
from src.schemas.record import RecordCreate
from src.bot.utils.utils import extract_data_from_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN_BOT")
# ToDo this domain will change all time need connect nginx for https
WEB_APP_URL = "https://managers-rugs-morris-tourism.trycloudflare.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)
    telegram_username = update.message.from_user.username
    first_name = update.message.from_user.first_name or "User"

    session = SessionLocal()
    try:
        user_repo = UserRepository(session)
        user = user_repo.get_by_telegram_id(telegram_id)

        if not user:
            temp_email = f"tg_{telegram_id}@telegram.user"
            temp_password = AuthService.hash_password(str(uuid.uuid4()))

            user = User(
                email=temp_email,
                name=first_name,
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                password=temp_password
            )
            user = user_repo.add(user)
            logger.info(f"Auto-created user for telegram_id {telegram_id}")
            welcome_msg = f"👋 Welcome {first_name}! Your account has been created."
        else:
            welcome_msg = f"👋 Welcome back {user.name}!"

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
            f"{welcome_msg}\n\nUse the buttons below to manage your finances:",
            reply_markup=keyboard
        )
        logger.info(f"User {telegram_id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred. Please try again.")
    finally:
        session.close()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)
    text = update.message.text

    # Skip status button and other non-financial messages
    if text in ["🔍 Check Status", "🔐 Open App"]:
        return

    session = SessionLocal()
    try:
        user_repo = UserRepository(session)
        user = user_repo.get_by_telegram_id(telegram_id)

        if not user:
            await update.message.reply_text(
                "⚠️ Please use /start command first to register."
            )
            return

        extracted_data = extract_data_from_messages(text)

        # Validate extracted data
        if not extracted_data or "amount" not in extracted_data:
            await update.message.reply_text(
                "❌ Could not understand your message. Please use format like:\n"
                "💰 50 for groceries\n"
                "💸 100 USD for rent"
            )
            return

        record_repo = RecordRepository(session)
        record_service = RecordService(record_repo)

        record_data = RecordCreate(
            amount=float(extracted_data["amount"]),
            description=extracted_data.get("description", "No description"),
            currency=extracted_data.get("currency", "USD")
        )

        record_service.create_record(user.id, record_data)
        await update.message.reply_text(
            f"✅ Record created: {float(extracted_data['amount'])} {extracted_data.get('currency', 'USD')} for {extracted_data.get('description', 'No description')}"
        )

    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again or use the web app."
        )
    finally:
        session.close()


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, message_handler))

if __name__ == "__main__":
    app.run_polling()
