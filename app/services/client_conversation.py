
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from app.models.db_models import Appointment, ConversationState
from app.utils.phone_utils import normalize_phone
from app.services.send_sms import send_sms
from app.services.scheduler import check_slot_availability, book_appointment, client_has_appointment_on_date
from app.services.polite_slot_suggester import suggest_polite_slots
from app.utils.smart_weekday_utils import get_next_weekday_date, get_available_times_for_date, get_booking_confidence_parts
import calendar





def get_booking_confidence(parsed):
    score = 0
    raw_dt = parsed.get("appointment_datetime", "")

    if not raw_dt:
        return 0

    if any(day in raw_dt.lower() for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        score += 1

    if any(str(h) in raw_dt for h in range(1,13)):  # crude hour clue
        score += 1

    if "am" in raw_dt.lower() or "pm" in raw_dt.lower():
        score += 1

    if any(month in raw_dt.lower() for month in [
        "january", "february", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december"
    ]):
        score += 1

    return score


def is_in_past(requested_datetime):
    now = datetime.utcnow()
    return requested_datetime < (now - timedelta(minutes=60))


def is_thank_you_message(body):
    return "thank" in body.lower()


def normalize_to_future(dt):
    """If parsed datetime is in the past, bump it forward to a plausible future time (e.g. same weekday next week)."""
    now = datetime.utcnow()
    if dt < now:
        dt += timedelta(days=7)
    return dt


def is_in_past(requested_datetime):
    now = datetime.utcnow()
    return requested_datetime < (now - timedelta(minutes=60))

def is_thank_you_message(body):
    return "thank" in body.lower()

def normalize_to_future(dt):
    now = datetime.utcnow()
    if dt < now:
        dt += timedelta(days=7)
    return dt

def get_booking_confidence(parsed):
    score = 0
    if parsed.get("appointment_datetime"): score += 1
    if parsed.get("client_name"): score += 1
    if parsed.get("service_type"): score += 1
    return score

def handle_client_message(session, owner, client, state, body, parsed):
    body = body.strip()
    print("🤖 handle_client_message invoked!")
    print("📨 Client message:", body)

    # ✅ Handle thank you logic
    if state and state.booking_complete and is_thank_you_message(body):
        print("Client sent thank you — no reply needed.")
        return

    # ⛳️ NEW: Prompt if intent is 'book_appointment' but missing datetime
    if parsed.get("intent") == "book_appointment" and not parsed.get("appointment_datetime"):
        send_sms(
            client.phone,
            "Sure! What day and time work best for you? I can check my calendar and get you booked."
        )
        return

    if parsed.get("appointment_datetime"):
        requested_str = parsed["appointment_datetime"]
        confidence, parts = get_booking_confidence_parts(parsed)

        # 🟥 Not enough info → Ask based on what’s missing
        if confidence < 4:
            if not parts["time"] and parts["day"]:
                send_sms(client.phone, f"Got it — what time {parts['day']} were you thinking? I’ll check what’s open for you!")
            elif not parts["day"] and parts["time"]:
                send_sms(client.phone, "Sure! What day works best for you? I’ll check availability right away.")
            elif not parts["am_pm"] and parts["time"] and parts["day"]:
                send_sms(client.phone, f"Just to double-check — did you mean {parts['time']}am or {parts['time']}pm? (I’m open 8am to 8pm).")
            else:
                send_sms(client.phone, "Can you let me know what day and time you were hoping for? I’ll check right away.")
            return

        # 🟨 Soft confirmation (3/4 present)
        if confidence == 3:
            send_sms(client.phone, f"Just to confirm — you meant {requested_str}, right?")
            return

        try:
            requested_datetime = date_parser.parse(requested_str, fuzzy=True)
            requested_datetime = normalize_to_future(requested_datetime)
        except Exception as e:
            print(f"⚠️ Failed to parse/normalize datetime from: {requested_str} → {e}")
            send_sms(client.phone, "Hmm, I couldn't figure out the time you mentioned. Can you try saying it like 'Monday at 2pm'?")
            return

        # 🚩 Check for past dates
        if is_in_past(requested_datetime):
            send_sms(
                client.phone,
                f"It looks like you're trying to book a past time ({requested_datetime.strftime('%A %B %d at %I:%M %p')}). "
                "Let me know a new time you'd like!"
            )
            return

        # 🚩 Check for existing appt on same day
        if client_has_appointment_on_date(session, client.id, requested_datetime):
            send_sms(
                client.phone,
                f"I see you're already scheduled for {requested_datetime.strftime('%A %B %d')}."
                " If you'd like to reschedule or add another time, just reply here."
            )
            return

        # ✅ Proceed to normal slot check
        if check_slot_availability(owner.id, client.id, requested_datetime, session):
            send_sms(client.phone, f"Would you like me to lock in your appointment for {requested_datetime.strftime('%A, %B %d at %I:%M %p')}? Reply 'yes' and I’ll lock it in!")
            return

        # ✅ Use polite slot suggestion flow
        polite_alts = suggest_polite_slots(owner.id, requested_datetime, session)
        if polite_alts:
            alt_text = ", ".join([dt.strftime("%A %I:%M %p") for dt in polite_alts])
            send_sms(client.phone, f"Unfortunately {requested_datetime.strftime('%A %I:%M %p')} is not available. I do have: {alt_text}. Let me know if any of these work!")
        else:
            send_sms(client.phone, "Unfortunately I don’t have any nearby availability at that time. Feel free to check the full calendar or let me know if you're flexible!")
        return

    # ✅ If no datetime parsed, fallback to smart weekday check
    for weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        if weekday.lower() in body.lower():
            target_date = get_next_weekday_date(weekday)
            open_slots = get_available_times_for_date(session, owner.id, target_date)
            if open_slots:
                readable = target_date.strftime("%A, %B %d")
                suggestions = "\n".join([f"- {slot}" for slot in open_slots])
                send_sms(client.phone, f"Were you looking to book for {readable}? I have:\n{suggestions}\nLet me know what works best — or you can check the full calendar here: https://107f-104-62-30-137.ngrok-free.app/book/abc123")
                return

    # ✅ Fallback if nothing useful was parsed
    today = datetime.utcnow().date()
    polite_alts = suggest_polite_slots(owner.id, today, session)
    if polite_alts:
        slot_str = ", ".join([dt.strftime("%A %I:%M %p") for dt in polite_alts])
        send_sms(client.phone, f"Here are some available times: {slot_str}. Let me know if any of these work!")
    else:
        send_sms(client.phone, "I'm currently fully booked today. Feel free to check the full calendar for more options.")



# NEW: helper to get available times for a given date
def get_available_times_for_date(session, owner_id, date_obj):
    from app.services.slot_generator_v2 import generate_slots_for_date
    from app.models.db_models import Appointment

    all_slots = generate_slots_for_date(owner_id, date_obj)
    taken = session.query(Appointment.appointment_datetime).filter(
        Appointment.owner_id == owner_id,
        Appointment.appointment_datetime.between(
            datetime.combine(date_obj, datetime.min.time()),
            datetime.combine(date_obj, datetime.max.time())
        )
    ).all()
    taken_times = set([appt[0] for appt in taken])

    available = [dt for dt in all_slots if dt not in taken_times]
    return available
