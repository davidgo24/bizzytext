# app/services/date_normalizer.py

from datetime import datetime, timedelta
import dateparser

def normalize_weekday_request(requested_datetime: datetime) -> datetime:
    """
    Given a parsed datetime (possibly ambiguous like 'Friday at 2pm'),
    resolve to the most likely upcoming date for that weekday.
    """

    now = datetime.now()

    # If parsed date is already in the future, keep it
    if requested_datetime.date() >= now.date():
        return requested_datetime

    # Otherwise roll forward to the next week
    weekday_target = requested_datetime.weekday()  # Monday = 0, Sunday = 6
    days_ahead = (weekday_target - now.weekday() + 7) % 7

    # If today is same weekday but we're past the time, move to next week
    if days_ahead == 0 and requested_datetime.time() <= now.time():
        days_ahead = 7

    next_date = now.date() + timedelta(days=days_ahead)
    normalized = datetime.combine(next_date, requested_datetime.time())

    return normalized
