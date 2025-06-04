from fastapi import APIRouter, Request
from app.db.database import get_session
from app.models.db_models import Owner, Client, Appointment
from app.services.ai_parser import parse_message
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

    statement = select(Owner).where(Owner.twilio_phone_number == to_number)
    owner = session.exec(statement).first()

    if not owner:
        return {"status": "error", "message": "Owner not found"}

    # Handle client record automatically
    statement = select(Client).where(Client.phone == from_number, Client.owner_id == owner.id)
    client = session.exec(statement).first()

    if not client:
        client = Client(name="Unknown", phone=from_number, owner_id=owner.id)
        session.add(client)
        session.commit()
        session.refresh(client)

    parsed = parse_message(message_body)
    print(f"AI parsed intent: {parsed}")

    if parsed["intent"] == "book_appointment" and parsed["appointment_datetime"]:
        appointment_dt = datetime.fromisoformat(parsed["appointment_datetime"])
        appointment = Appointment(
            client_id=client.id,
            appointment_datetime=appointment_dt,
            service_type=parsed.get("service_type")
        )
        session.add(appointment)
        session.commit()

        # ✅ Autopilot confirmation to Owner
        confirmation_message = (
            f"✅ Auto-booked {client.name} ({client.phone}) on "
            f"{appointment_dt.strftime('%A %B %d at %I:%M %p')}."
            "\n\nReply if any changes are needed."
        )
        send_sms(owner.personal_phone_number, confirmation_message)

        return {"status": "booked", "appointment": appointment_dt.isoformat()}

    # For other intents, notify owner for manual review
    generic_message = (
        f"Client texted: \"{message_body}\"\n"
        f"Intent: {parsed['intent']}\n"
        "No booking made. Please review."
    )
    send_sms(owner.personal_phone_number, generic_message)

    return {"status": "forwarded", "intent": parsed["intent"]}
