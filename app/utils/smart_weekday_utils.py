from datetime import datetime, timedelta
from app.services.slot_generator_v2 import generate_slots_for_date
from app.services.scheduler import check_slot_availability
import re

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

def get_next_weekday_date(target_weekday: str) -> datetime.date:
    """Return the next occurrence of the given weekday within a 7-day window."""
    target_weekday = target_weekday.lower()
    if target_weekday not in WEEKDAYS:
        raise ValueError(f"Invalid weekday: {target_weekday}")

    today = datetime.utcnow().date()
    today_idx = today.weekday()
    target_idx = WEEKDAYS[target_weekday]

    days_ahead = (target_idx - today_idx + 7) % 7
    if days_ahead == 0:
        days_ahead = 7  # Always go forward, never today

    return today + timedelta(days=days_ahead)

def get_available_times_for_date(owner_id: int, target_date: datetime.date, session) -> list[datetime]:
    """Return a list of available datetime slots for a given date, filtered against booked appointments."""
    slots = generate_slots_for_date(owner_id, target_date)
    available = []
    for dt in slots:
        if check_slot_availability(owner_id, None, dt, session):
            available.append(dt)
    return available


def get_booking_confidence_parts(parsed):
    raw = parsed.get("appointment_datetime", "")
    parts = {
        "day": None,
        "time": None,
        "am_pm": None,
        "date": None,
    }

    # Heuristics to check what we can infer
    day_match = re.search(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", raw, re.IGNORECASE)
    if day_match:
        parts["day"] = day_match.group(0)

    time_match = re.search(r"\b([1-9]|1[0-2])(?::[0-5][0-9])?\b", raw)
    if time_match:
        parts["time"] = time_match.group(0)

    if "am" in raw.lower() or "pm" in raw.lower():
        parts["am_pm"] = "am" if "am" in raw.lower() else "pm"

    date_match = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}\b", raw)
    if date_match:
        parts["date"] = date_match.group(0)

    confidence = sum(1 for v in parts.values() if v is not None)
    return confidence, parts