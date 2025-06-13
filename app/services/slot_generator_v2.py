from datetime import datetime, timedelta, time
from app.services.owner_schedule_service import get_owner_schedule_for_date
from app.models.db_models import Appointment

SLOT_LENGTH_MINUTES = 60
CUTOFF_MINUTES = 30

def generate_slots_for_date(owner_id, target_date, session):
    print(f"🔍 Generating slots for {target_date}")
    slot_datetimes = []

    blocks = get_owner_schedule_for_date(owner_id, target_date, session)
    print(f"📅 Schedule blocks for {target_date}: {blocks}")

    now = datetime.now()
    cutoff_time = now + timedelta(minutes=CUTOFF_MINUTES)

    for block in blocks:
        current_slot = datetime.combine(target_date, block.block_start)

        while current_slot.time() < block.block_end:
            # 🛡️ Skip if the slot is too soon or in the past (today only)
            if target_date == now.date() and current_slot < cutoff_time:
                current_slot += timedelta(minutes=SLOT_LENGTH_MINUTES)
                continue

            # 🚫 Check for conflicts
            conflict = session.query(Appointment).filter(
                Appointment.owner_id == owner_id,
                Appointment.appointment_datetime == current_slot
            ).first()

            if not conflict:
                slot_datetimes.append(current_slot)

            current_slot += timedelta(minutes=SLOT_LENGTH_MINUTES)

    # ✅ Sort slots by time, then format
    slot_datetimes.sort()
    formatted_slots = [dt.strftime("%I:%M %p") for dt in slot_datetimes]

    print(f"✅ Final slots for {target_date}: {formatted_slots}")
    return formatted_slots
