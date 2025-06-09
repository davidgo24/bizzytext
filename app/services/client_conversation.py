from datetime import datetime
from dateutil import parser as date_parser
from app.services.scheduler import check_slot_availability, book_appointment, suggest_alternate_slots, client_has_appointment_on_date
from app.services.send_sms import send_sms
from app.services.offered_slots_state import save_offered_slots, get_offered_slots
from app.services.date_normalizer import normalize_weekday_request




def is_thank_you_message(body):
    return "thank" in body.lower()

def handle_client_message(session, owner, client, state, body, parsed):
    body = body.strip()

    if state.booking_complete and is_thank_you_message(body):
        print("Client sent thank you — no reply needed.")
        return

    if parsed.get("appointment_datetime"):
        requested_str = parsed["appointment_datetime"]
        requested_datetime = date_parser.parse(requested_str)
        # Normalize
        requested_datetime = normalize_weekday_request(requested_datetime)

        # If slot available → book immediately
        if check_slot_availability(owner.id, client.id, requested_datetime, session):
            booked = book_appointment(session, owner, client, state, requested_datetime)
            send_sms(client.phone, f"✅ You're all set for {booked.appointment_datetime.strftime('%A %I:%M %p')}.")
            send_sms(owner.personal_phone_number, f"📅 New appointment booked: {client.name or client.phone} - {booked.appointment_datetime.strftime('%A %I:%M %p')}")
            return

        # Otherwise, suggest alternatives dynamically
        alternatives = suggest_alternate_slots(owner.id, requested_datetime, session)
        alt_text = ", ".join([dt.strftime("%A %I:%M %p") for dt in alternatives])

        send_sms(client.phone, f"Unfortunately {requested_datetime.strftime('%A %I:%M %p')} is not available. I do have: {alt_text}. Let me know if any of these work!")

        # 💾 Save the alternatives offered
        save_offered_slots(session, state, alternatives)
        return

