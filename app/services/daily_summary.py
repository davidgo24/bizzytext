from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.db_models import Appointment, Client, Owner
from sqlalchemy import func


def get_todays_appointments():
    session = get_session()

    # Safe timezone handling

    today_date = datetime.now().date()

    appointments = session.exec(
        select(Appointment).where(
            func.date(Appointment.appointment_datetime) == today_date
        )
    ).all()

    if not appointments:
        print("📅 No appointments scheduled for today.")
        return

    print(f"\n📅 Appointments for {today_date.strftime('%A %B %d, %Y')}:\n")
    
    for appt in appointments:
        client = session.get(Client, appt.client_id)
        owner = session.get(Owner, client.owner_id)

        print(f"🧑 Client: {client.name or 'Unknown'}")
        print(f"📅 Time: {appt.appointment_datetime.strftime('%I:%M %p')}")
        print(f"✂️ Service: {appt.service_type or 'Unknown'}")
        print(f"👤 Owner: {owner.name}")
        print("-" * 30)

if __name__ == "__main__":
    get_todays_appointments()
