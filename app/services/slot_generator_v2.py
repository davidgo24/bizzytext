from datetime import datetime, timedelta, time
from app.services.owner_schedule_service import get_owner_schedule_for_date
from app.models.db_models import Appointment
from app.db.database import get_session

SLOT_LENGTH_MINUTES = 60

def generate_slots_for_date(owner_id, target_date, session):
    from datetime import datetime, timedelta

    print(f"🔍 Generating slots for {target_date}")
    slots = []

    blocks = get_owner_schedule_for_date(owner_id, target_date, session)
    print(f"📅 Schedule blocks for {target_date}: {blocks}")

    for block in blocks:
        current_slot = datetime.combine(target_date, block.block_start)

        while current_slot.time() < block.block_end:
            conflict = session.query(Appointment).filter(
                Appointment.owner_id == owner_id,
                Appointment.appointment_datetime == current_slot
            ).first()

            if not conflict:
                formatted = current_slot.strftime("%I:%M %p")
                slots.append(formatted)

            current_slot += timedelta(minutes=60)

    print(f"✅ Final slots for {target_date}: {slots}")
    return slots