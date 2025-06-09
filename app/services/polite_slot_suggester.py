# app/services/polite_slot_suggester.py

from datetime import datetime, timedelta
from app.services.slot_generator_v2 import generate_slots_for_date
from app.services.scheduler import check_slot_availability

# Configurable time buffer (per industry later)
POLITE_BUFFER_MINUTES = 60
MAX_SLOTS_TO_SUGGEST = 3

def suggest_polite_slots(owner_id, requested_datetime, session):
    """
    Return polite alternate slots for the client based on requested date.
    """
    today = datetime.utcnow().date()
    if isinstance(requested_datetime, datetime):
        requested_date = requested_datetime.date()
    else:
        requested_date = requested_datetime


    # Only fetch slots if requested date is today or later
    if requested_date < today:
        return []

    # Generate full slots for requested day
    raw_slots = generate_slots_for_date(owner_id, requested_date, session)

    polite_cutoff = datetime.utcnow() + timedelta(minutes=POLITE_BUFFER_MINUTES)

    polite_slots = []
    for slot_str in raw_slots:
        slot_time = datetime.strptime(slot_str, "%I:%M %p").time()
        candidate_dt = datetime.combine(requested_date, slot_time)

        # Only offer slots:
        # 1️⃣ Not in the past
        # 2️⃣ At least POLITE_BUFFER_MINUTES away if same day
        if candidate_dt >= polite_cutoff:
            if check_slot_availability(owner_id, None, candidate_dt, session):
                polite_slots.append(candidate_dt)

    return polite_slots[:MAX_SLOTS_TO_SUGGEST]
