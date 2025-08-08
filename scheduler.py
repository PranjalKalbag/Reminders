from datetime import datetime, timedelta
from bot import send_telegram_message  # avoid circular imports
import pytz
import requests

TELEGRAM_API_URL = "http://127.0.0.1:8000/reminders/search"  # your FastAPI API
TIMEZONE = pytz.timezone("Asia/Kolkata")  # adjust if needed

def send_due_reminders(source="cron"):
    now = datetime.now(TIMEZONE)
    params = {"date": now.date().isoformat()}

    try:
        resp = requests.get(TELEGRAM_API_URL, params=params)
        if resp.status_code != 200:
            send_telegram_message("⚠️ Couldn't fetch reminders.")
            return

        reminders = resp.json()
        # filter only reminders after current time
        reminders = [
            r for r in reminders
            if "time" in r and r["time"] and r["time"] > now.strftime("%H:%M:%S")
        ]
        prefix = ""
        if source == "startup":
            prefix = "🚀 *App Starting Up*\n"
        elif source == "cron":
            prefix = "⏰ *Scheduled Reminder*\n"
        if reminders:
            
            for r in reminders:
                send_telegram_message(f"{prefix}\n🕒 {r['title']} - {r['description']}")
        else:
            send_telegram_message(f"{prefix}\n✅ No due reminders at {now.strftime('%H:%M')}")
    except Exception as e:
        send_telegram_message(f"❌ Error sending reminders: {e}")


def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    # Run every day at 2 PM and 8 PM
    scheduler.add_job(send_due_reminders, "cron", hour=9, minute=0, kwargs={"source": "cron"})
    scheduler.add_job(send_due_reminders, "cron", hour=13, minute=0, kwargs={"source": "cron"})

    # Run once after startup (5 sec delay)
    scheduler.add_job(
        send_due_reminders,
        "date",
        run_date=datetime.now(TIMEZONE) + timedelta(seconds=5), kwargs={"source": "startup"}
    )

    scheduler.start()