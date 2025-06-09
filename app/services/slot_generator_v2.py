from datetime import datetime, timedelta, time
from app.services.owner_schedule_service import get_owner_schedule_for_date
from app.models.db_models import Appointment
from app.db.database import get_session

SLOT_LENGTH_MINUTES = 60

def generate_slots_for_date(owner_id, target_date):
    session = get_session()
    slots = []

    # pull the owner's schedule blocks for that date
    blocks = get_owner_schedule_for_date(owner_id, target_date)

    for block in blocks:
        current_slot = datetime.combine(target_date, block.block_start)

        while current_slot.time() < block.block_end:
            # Check for conflicts (appointments that already exist)
            conflict = session.query(Appointment).filter(
                Appointment.owner_id == owner_id,
                Appointment.appointment_datetime == current_slot
            ).first()

            if not conflict:
                slots.append(current_slot.strftime("%I:%M %p"))

            current_slot += timedelta(minutes=SLOT_LENGTH_MINUTES)

    return slots
