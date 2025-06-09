from datetime import datetime
from dateutil import parser as date_parser
from app.models.db_models import Appointment, ConversationState
from app.utils.phone_utils import normalize_phone
from app.services.send_sms import send_sms
from app.services.scheduler import check_slot_availability, book_appointment, client_has_appointment_on_date
from app.services.polite_slot_suggester import suggest_polite_slots
from datetime import timedelta


def is_in_past(requested_datetime):
    now = datetime.utcnow()
    return requested_datetime < (now - timedelta(minutes=60))


def is_thank_you_message(body):
    return "thank" in body.lower()

def handle_client_message(session, owner, client, state, body, parsed):
    body = body.strip()

    # ✅ Handle thank you logic
    if state and state.booking_complete and is_thank_you_message(body):
        print("Client sent thank you — no reply needed.")
        return

        # ✅ Handle AI-parsed appointment intent
    if parsed.get("appointment_datetime"):
        requested_str = parsed["appointment_datetime"]
        requested_datetime = date_parser.parse(requested_str)

        if isinstance(requested_datetime, str):
            requested_datetime = date_parser.parse(requested_datetime)

        # 🚩 Check for past dates
        if is_in_past(requested_datetime):
            send_sms(
                client.phone,
                f"It looks like you're trying to book a past time ({requested_datetime.strftime('%A %B %d at %I:%M %p')}). "
                "Let me know a new time you'd like!"
            )
            return

        # 🚩 Check for any existing appt same day (not just exact time)
        if client_has_appointment_on_date(session, client.id, requested_datetime):
            send_sms(
                client.phone,
                f"I see you're already scheduled for {requested_datetime.strftime('%A %B %d')}."
                " If you'd like to reschedule or add another time, just reply here."
            )
            return

        # ✅ Proceed to normal slot check
        if check_slot_availability(owner.id, client.id, requested_datetime, session):
            booked = book_appointment(session, owner, client, state, requested_datetime)

            send_sms(client.phone, f"✅ You're all set for {booked.appointment_datetime.strftime('%A %B %d at %I:%M %p')}.")
            send_sms(owner.personal_phone_number, f"📅 New appointment booked: {client.name or client.phone} - {booked.appointment_datetime.strftime('%A %B %d at %I:%M %p')}")
            return

        # ✅ Use polite slot suggestion flow
        polite_alts = suggest_polite_slots(owner.id, requested_datetime, session)

        if polite_alts:
            alt_text = ", ".join([dt.strftime("%A %I:%M %p") for dt in polite_alts])
            send_sms(client.phone, f"Unfortunately {requested_datetime.strftime('%A %I:%M %p')} is not available. I do have: {alt_text}. Let me know if any of these work!")
        else:
            send_sms(client.phone, "Unfortunately I don’t have any nearby availability at that time. Feel free to check the full calendar or let me know if you're flexible!")

        return

    # ✅ Fallback if nothing was parsed at all
    today = datetime.utcnow().date()
    # And for fallback when nothing was parsed:
    polite_alts = suggest_polite_slots(owner.id, today, session)

    if polite_alts:
        slot_str = ", ".join([dt.strftime("%A %I:%M %p") for dt in polite_alts])
        send_sms(client.phone, f"Here are some available times: {slot_str}. Let me know if any of these work!")
    else:
        send_sms(client.phone, "I'm currently fully booked today. Feel free to check the full calendar for more options.")
