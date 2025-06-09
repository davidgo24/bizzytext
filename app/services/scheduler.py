from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db_models import Appointment
from app.services.slot_generator_v2 import generate_slots_for_date
from app.services.owner_schedule_service import get_owner_schedule_for_date

SLOT_LENGTH_MINUTES = 60

def check_slot_availability(owner_id, client_id, requested_datetime, session: Session):
    # Check if any appointment exists at that exact datetime
    return session.query(Appointment).filter(
        Appointment.appointment_datetime == requested_datetime
    ).first() is None

def client_has_appointment_on_date(session, client_id, requested_datetime):
    return session.query(Appointment).filter(
        Appointment.client_id == client_id,
        func.date(Appointment.appointment_datetime) == requested_datetime.date()
    ).first() is not None

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

def suggest_alternate_slots(owner_id, requested_datetime, session: Session, days_ahead=2):
    suggestions = []
    for offset in range(0, days_ahead + 1):
        target_date = requested_datetime.date() + timedelta(days=offset)
        slots = generate_slots_for_date(owner_id, target_date)
        for slot_dt in slots:
            if check_slot_availability(owner_id, None, slot_dt, session):
                suggestions.append(slot_dt)
    return suggestions
