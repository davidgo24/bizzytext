from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.models.db_models import Appointment
from app.services.slot_generator import generate_slots_for_date

SLOT_LENGTH_MINUTES = 60

def check_slot_availability(owner_id, client_id, requested_datetime, session):
    existing = session.query(Appointment).filter(
        Appointment.client_id == client_id,
        Appointment.appointment_datetime == requested_datetime
    ).first()
    return existing is None

def book_appointment(session, owner, client, state, requested_datetime):
    appointment = Appointment(
        client_id=client.id,
        appointment_datetime=requested_datetime,
        service_type=None
    )
    session.add(appointment)
    session.delete(state)
    session.commit()
    return appointment

def suggest_alternate_slots(owner_id, client_id, requested_datetime: datetime, session: Session, days_ahead=2):
    suggestions = []
    for offset in range(0, days_ahead + 1):
        target_date = requested_datetime.date() + timedelta(days=offset)
        slots = generate_slots_for_date(target_date)
        for slot in slots:
            slot_dt = datetime.combine(target_date, datetime.strptime(slot, "%I:%M %p").time())
            if check_slot_availability(owner_id, client_id, slot_dt, session):
                suggestions.append(slot_dt)
    return suggestions
