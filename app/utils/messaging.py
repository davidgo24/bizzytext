from datetime import datetime
import calendar
import os
from app.services.send_sms import send_sms
from app.models.db_models import Owner
from sqlalchemy.orm import Session

def format_dt_human(dt: datetime) -> str:
    # Format time in a user-friendly way depending on OS
    if os.name == "nt":  # Windows
        return dt.strftime("%A at %#I:%M %p")
    else:  # Mac/Linux
        return dt.strftime("%A at %-I:%M %p")

def notify_bizzy_about_new_web_booking(client_name: str, client_phone: str, appointment_datetime: datetime, owner: Owner, db: Session):
    formatted_time = format_dt_human(appointment_datetime)

    client_msg = f"✅ You’re confirmed for {formatted_time}. Reply here if you need to reschedule."
    owner_msg = f"📅 New booking from {client_name} for {formatted_time}. You can reply here if needed."

    send_sms(client_phone, client_msg)
    send_sms(owner.personal_phone_number, owner_msg)
