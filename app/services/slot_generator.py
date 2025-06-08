from datetime import datetime, timedelta, time

def generate_slots_for_date(date_requested, slot_length=60, start_hour=9, end_hour=17):
    slots = []
    current = datetime.combine(date_requested, time(start_hour, 0))
    end_time = datetime.combine(date_requested, time(end_hour, 0))

    while current <= end_time:
        slots.append(current.strftime("%I:%M %p"))
        current += timedelta(minutes=slot_length)
    
    return slots