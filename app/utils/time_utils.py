from datetime import datetime

def format_human_date(dt: datetime) -> str:
    return dt.strftime("%A at %-I:%M %p")  # e.g. "Friday at 2:00 PM"
