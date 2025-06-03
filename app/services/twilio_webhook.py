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
    from_number = normalize_phone(form.get("From"))
    to_number = normalize_phone(form.get("To"))
    message_body = form.get("Body")

    session = get_session()

    # Match Owner based on Twilio number (To)
    statement = select(Owner).where(Owner.twilio_phone_number == to_number)
    owner = session.exec(statement).first()

    if not owner:
        return {"status": "error", "message": "Owner not found"}

    parsed = parse_owner_message(message_body)

    # Check if client exists
    statement = select(Client).where(Client.name == parsed['client_name'], Client.owner_id == owner.id)
    client = session.exec(statement).first()

    if not client:
        client = Client(name=parsed['client_name'], phone="unknown", owner_id=owner.id)
        session.add(client)
        session.commit()
        session.refresh(client)

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

    send_sms(owner.twilio_phone_number, confirmation_message)

    return {
        "status": "received",
        "client": client.name,
        "appointment": appointment.appointment_datetime.isoformat()
    }
