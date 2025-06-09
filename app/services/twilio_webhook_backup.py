# app/services/twilio_webhook.py

from fastapi import APIRouter, Request
from app.db.database import get_session
from app.models.db_models import Owner, Client, Appointment
from app.services.ai_parser import parse_owner_message
from app.services.scheduler import schedule_reminder
from app.services.send_sms import send_sms
from app.utils.phone_utils import normalize_phone
from datetime import datetime
from sqlmodel import select

router = APIRouter()

@router.post("/twilio-webhook")
async def receive_sms(request: Request):
    form = await request.form()
    from_number = form.get("From")
    to_number = form.get("To")
    message_body = form.get("Body")

    session = get_session()

    # Normalize phone numbers
    normalized_to = normalize_phone(to_number)
    normalized_from = normalize_phone(from_number)

    # Lookup Owner by Twilio number (To field)
    statement = select(Owner).where(Owner.twilio_phone_number == normalized_to)
    owner = session.exec(statement).first()

    if not owner:
        return {"status": "error", "message": "Owner not found"}

    # Handle client message
    print(f"Client message received: {normalized_from} said '{message_body}'")

    parsed = parse_owner_message(message_body)

    # Lookup client by phone number under this owner
    statement = select(Client).where(Client.phone == normalized_from, Client.owner_id == owner.id)
    client = session.exec(statement).first()

    if not client:
        # fallback for missing client name
        name = parsed['client_name'] if parsed['client_name'] else f"Client {normalized_from[-4:]}"
        client = Client(name=name, phone=normalized_from, owner_id=owner.id)
        session.add(client)
        session.commit()
        session.refresh(client)

    # Schedule appointment if date was parsed
    if parsed['appointment_datetime']:
        appointment_dt = datetime.fromisoformat(parsed['appointment_datetime'])
        appointment = Appointment(
            client_id=client.id,
            appointment_datetime=appointment_dt,
            service_type=parsed['service_type']
        )
        session.add(appointment)
        session.commit()

        schedule_reminder(appointment_dt, client.phone)

        confirmation_message = (
            f"✅ Appointment booked: {client.name} on {appointment_dt.strftime('%A %B %d at %I:%M %p')}."
        )
        send_sms(owner.personal_phone_number, confirmation_message)
    else:
        # fallback message when no appointment parsed
        send_sms(owner.personal_phone_number, f"New message from {client.name}: '{message_body}'")

    return {
        "status": "received",
        "client": client.name,
        "owner": owner.name
    }
