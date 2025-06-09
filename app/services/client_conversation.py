from datetime import datetime, timedelta, time
from dateutil import parser as date_parser
from app.models.db_models import Appointment, ConversationState
from app.utils.phone_utils import normalize_phone
from app.services.send_sms import send_sms
from app.services.scheduler import check_slot_availability, book_appointment, suggest_alternate_slots, client_has_appointment_on_date

def is_thank_you_message(body):
    return "thank" in body.lower()

def handle_client_message(session, owner, client, state, body, parsed):
    body = body.strip()

    # ✅ Handle thank you logic
    if state.booking_complete and is_thank_you_message(body):
        print("Client sent thank you — no reply needed.")
        return

    if parsed.get("appointment_datetime"):
        requested_str = parsed["appointment_datetime"]
        requested_datetime = date_parser.parse(requested_str)

        if isinstance(requested_datetime, str):
            requested_datetime = date_parser.parse(requested_datetime)

        # ✅ FIRST: check if client already has appointment that day
        if client_has_appointment_on_date(session, client.id, requested_datetime):
            send_sms(
                client.phone,
                f"I see you're already scheduled for {requested_datetime.strftime('%A')}."
                " If you'd like to reschedule, just reply here."
            )
            return

        # ✅ THEN check if requested slot itself is free
        if check_slot_availability(owner.id, client.id, requested_datetime, session):
            booked = book_appointment(session, owner, client, state, requested_datetime)

            send_sms(client.phone, f"✅ You're all set for {booked.appointment_datetime.strftime('%A %I:%M %p')}.")
            send_sms(owner.personal_phone_number, f"📅 New appointment booked: {client.name or client.phone} - {booked.appointment_datetime.strftime('%A %I:%M %p')}")
            return

        # ✅ Finally suggest alternatives
        alternatives = suggest_alternate_slots(owner.id, requested_datetime, session)
        alt_text = ", ".join([dt.strftime("%A %I:%M %p") for dt in alternatives])

        send_sms(client.phone, f"Unfortunately {requested_datetime.strftime('%A %I:%M %p')} is not available. I do have: {alt_text}. Let me know if any of these work!")
        return
    

    # ✅ Fallback — still missing info
    today = datetime.utcnow().date()
    slots = generate_slots_for_date(owner.id, today)
    slot_str = ", ".join(slots[:3])
    send_sms(
        client.phone,
        f"Available times today include: {slot_str}. Please reply with a time or check full calendar: [link]"
    )
    return
