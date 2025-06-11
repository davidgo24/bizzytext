from datetime import datetime
import calendar
from app.services.send_sms import send_sms  # 🔁 Update path to match your structure
from app.models.db_models import Owner
from sqlalchemy.orm import Session
import os



def format_dt_human(dt: datetime) -> str:
    weekday = calendar.day_name[dt.weekday()]
    time_str = dt.strftime("%-I:%M %p")  # Works on Mac/Linux
    return f"{weekday} at {time_str}"



def notify_bizzy_about_new_web_booking(client_name: str, client_phone: str, appointment_datetime: datetime, owner: Owner, db: Session):
    # Format datetime string depending on OS
    if os.name == "nt":  # Windows
        formatted_time = appointment_datetime.strftime("%A at %#I:%M %p")
    else:  # Mac/Linux
        formatted_time = appointment_datetime.strftime("%A at %-I:%M %p")

    # Message to client
    client_msg = f"✅ You’re confirmed for {formatted_time}. Reply here if you need to reschedule."

    # Message to owner
    owner_msg = f"📅 New booking from {client_name} for {formatted_time}. You can reply here if needed."

    # Send both SMS messages
    send_sms(client_phone, client_msg)
    send_sms(owner.personal_phone_number, owner_msg)

    # (Optional future hook: update ConversationState.booking_complete = True)
