# app/services/scheduler.py

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+ timezone module

from sqlmodel import Session, select
from app.db.database import get_session
from app.models.db_models import Appointment, Client, Owner
from app.services.send_sms import send_sms

# Set barber timezone here (adjust as needed)
OWNER_TIMEZONE = ZoneInfo("America/Los_Angeles")

def schedule_reminders():
    session = get_session()
    now = datetime.now(OWNER_TIMEZONE)

    appointments = session.exec(select(Appointment)).all()

    print(f"⏰ Current system time: {now.isoformat()}", flush=True)



    for appt in appointments:
        client = session.get(Client, appt.client_id)
        owner = session.get(Owner, client.owner_id)

        # Convert appointment datetime to timezone-aware
        appt_dt = appt.appointment_datetime.replace(tzinfo=OWNER_TIMEZONE)

        reminders_sent = appt.reminders_sent or ""
        has_night_before = "night_before" in reminders_sent
        has_same_day = "same_day" in reminders_sent

        # ✅ NIGHT BEFORE LOGIC (runs any time after 7PM previous day)
        if not has_night_before:
            night_cutoff = appt_dt - timedelta(days=1)
            if now.date() == night_cutoff.date() and now.hour >= 19:
                send_sms(
                    client.phone,
                    f"✅ Reminder: Your appointment is tomorrow at {appt_dt.strftime('%I:%M %p')}."
                )
                appt.reminders_sent = (reminders_sent + "night_before,").strip(",")
                session.add(appt)
                session.commit()
                print(f"✅ Night before reminder sent for appointment {appt.id}.")

        # ✅ SAME DAY LOGIC (runs morning of appointment anytime after midnight)
        if not has_same_day and appt_dt.date() == now.date():
            send_sms(
                client.phone,
                f"📅 You're scheduled for {appt_dt.strftime('%I:%M %p')} today.\n\nArriving on time allows for your best cut, keeps everyone's schedule smooth, and helps us run a sustainable shop. 🙏 If you need to cancel or reschedule, reply here as early as possible."
            )
            appt.reminders_sent = (reminders_sent + "same_day,").strip(",")
            session.add(appt)
            session.commit()
            print(f"✅ Same day reminder sent for appointment {appt.id}.")
