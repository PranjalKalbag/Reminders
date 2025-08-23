import os
import requests
from datetime import datetime as dt
from datetime import date
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,ConversationHandler, CallbackContext

from dotenv import load_dotenv
load_dotenv()


BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

bot = Bot(token=BOT_TOKEN)


def is_authorized(update):
    return update.effective_user.id == TELEGRAM_ID

def help(update, context):

    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/today - View today's reminders\n"
        "/add - Add a new reminder\n"
        "/cancel - Cancel the current operation\n"
    )

def start(update, context):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    update.message.reply_text("👋 Welcome back!")

def send_telegram_message(message: str):
    bot.send_message(chat_id=TELEGRAM_ID, text=message, parse_mode="Markdown")

def today(update, context):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    try:
        response = requests.get("http://127.0.0.1:8000/reminders/search", params={"date":date.today().isoformat()})
        if response.status_code != 200:
            update.message.reply_text("⚠️ Couldn't fetch reminders.")
            return

        reminders = response.json()
        if not reminders:
            update.message.reply_text("✅ No reminders for today.")
            return

        message = "📅 *Today's Reminders:*\n\n"
        for r in reminders:
            message += f"🕒 {r['title']}-{r['description']} \n"

        update.message.reply_text(message, parse_mode="Markdown")

    
    except Exception as e:
        update.message.reply_text("❌ Error fetching reminders.")
        print(f'Error msg: {e}')
    
def start_add(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return 

    update.message.reply_text("📝 What is the *title* of your reminder?", parse_mode="Markdown")
    return TITLE

def get_title(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    context.user_data["title"] = update.message.text
    update.message.reply_text("✏️ Add a *description* for your reminder:", parse_mode="Markdown")
    return DESCRIPTION

def get_description(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    context.user_data["description"] = update.message.text
    update.message.reply_text("📅 Enter the *start date* (YYYY-MM-DD):", parse_mode="Markdown")
    return START_DATE

def get_start_date(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    context.user_data["start_date"] = update.message.text
    update.message.reply_text("📆 Enter the *end date* (YYYY-MM-DD):", parse_mode="Markdown")
    return END_DATE

def get_end_date(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    context.user_data["end_date"] = update.message.text
    text = update.message.text.strip().lower()
    if text in ("", "skip", "none"):
        context.user_data["end_date"] = None
    else:
        context.user_data["end_date"] = text 
    # Send data to backend
    payload = {
        "user_id": TELEGRAM_ID,
        "title": context.user_data["title"],
        "description": context.user_data["description"],
        "start_date": context.user_data["start_date"],
        "end_date": context.user_data["end_date"],
    }

    try:
        response = requests.post(f"http://127.0.0.1:8000/input", json=payload)
        if response.status_code == 200:
            update.message.reply_text("✅ Reminder added successfully!")
        else:
            update.message.reply_text("⚠️ Failed to add reminder.")
    except Exception as e:
        update.message.reply_text("❌ Error talking to backend.")
        print(f"Error: {e}")

    return ConversationHandler.END

def cancel(update, context: CallbackContext):
    if not is_authorized(update):
        update.message.reply_text("❌ Access denied.")
        return
    update.message.reply_text("🚫 Reminder creation cancelled.")
    return ConversationHandler.END

TITLE, DESCRIPTION, START_DATE, END_DATE = range(4)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("help", help))
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add', start_add)],
    states={
        TITLE: [MessageHandler(Filters.text & ~Filters.command, get_title)],
        DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, get_description)],
        START_DATE: [MessageHandler(Filters.text & ~Filters.command, get_start_date)],
        END_DATE: [MessageHandler(Filters.text & ~Filters.command, get_end_date)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
