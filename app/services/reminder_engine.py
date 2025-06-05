import os
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.db_models import Appointment, Client, Owner
from app.services.send_sms import send_sms
from dotenv import load_dotenv

load_dotenv(".env_template")

def send_reminder(appointment_id: int):
    session = get_session()

    appointment = session.exec(select(Appointment).where(Appointment.id == appointment_id)).first()
    client = session.exec(select(Client).where(Client.id == appointment.client_id)).first()
    owner = session.exec(select(Owner).where(Owner.id == client.owner_id)).first()

    reminder_msg = (
        f"⏰ Reminder: You have an appointment tomorrow at {appointment.appointment_datetime.strftime('%I:%M %p')} with {owner.name}. "
        f"Reply here if you need to cancel or reschedule."
    )
    send_sms(client.phone, reminder_msg)

    appointment.reminders_sent = (appointment.reminders_sent or "") + "night_before,"
    session.commit()

    owner_msg = (
        f"📢 Reminder sent to {client.name or client.phone} for {appointment.appointment_datetime.strftime('%A %I:%M %p')}."
    )
    send_sms(owner.personal_phone_number, owner_msg)

    print(f"✅ Reminder sent for appointment {appointment_id}.")
