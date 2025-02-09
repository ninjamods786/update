import random
import string
import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "7601607062:AAH-pP3LQdjKwH8eGpiPV4vNef1SvRKFAzA"
ADMIN_IDS = ["1240179115"]

user_attacks = {}
users = {}
keys = {}
pending_key_requests = {}
pending_target_requests = {}

def generate_key(length=10):
    """Generates a random key of the given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a menu with all available options."""
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton("\U0001F3AE Set Target (BGMI)"),
                KeyboardButton("⚔️ Start Attack"),
            ],
            [
                KeyboardButton("⛔ Stop Attack"),
                KeyboardButton("🗝️ Generate Key"),
            ],
            [
                KeyboardButton("❌ Remove User"),
                KeyboardButton("Contact admin✔️"),
            ],
        ],
    )
    await update.message.reply_text("🔹 Choose an option from the menu below:", reply_markup=markup)

async def ask_key_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if user_id in ADMIN_IDS:
        await update.message.reply_text("Enter the time duration for the key (e.g., `2 hours`, `5 days`):")
        pending_key_requests[user_id] = True
    else:
        await update.message.reply_text("❌ Only admins can generate keys.")

async def generate_and_show_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if user_id in ADMIN_IDS and user_id in pending_key_requests:
        duration_input = update.message.text
        try:
            if 'hour' in duration_input:
                hours = int(duration_input.split()[0])
                expiration_time = add_time_to_current_date(hours=hours)
            elif 'day' in duration_input:
                days = int(duration_input.split()[0])
                expiration_time = add_time_to_current_date(days=days)
            else:
                await update.message.reply_text("❌ Invalid duration. Please use 'hours' or 'days'.")
                return

            key = generate_key()
            
            keys[key] = expiration_time

            await update.message.reply_text(f"✅ Generated key: `{key}`\nValid until: {expiration_time}", parse_mode="Markdown")
            del pending_key_requests[user_id]

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("❌ Only admins can generate keys.")

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    if user_input == "🎮 Set Target (BGMI)":
        await ask_target_details(update, context)
    elif user_input == "⚔️ Start Attack":
        await start(update, context)
    elif user_input == "⛔ Stop Attack":
        await stop(update, context)
    elif user_input == "🗝️ Generate Key":
        await ask_key_duration(update, context)
    elif user_input == "❌ Remove User":
        await update.message.reply_text("Send /remove <user_id> to remove a user.")
    elif user_input == "Contact admin✔️":
        await update.message.reply_text("Please contact the admin at @NINJAGAMEROP")

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection))
    
    application.run_polling()

if __name__ == '__main__':
    main()
