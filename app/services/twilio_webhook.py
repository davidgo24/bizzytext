# app/services/twilio_webhook.py

from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import PlainTextResponse
from app.db.database import get_session
from app.models.db_models import Owner, Client, Appointment, ConversationState
from app.services.ai_parser import parse_message, parse_owner_message
from app.utils.phone_utils import normalize_phone
from app.services.send_sms import send_sms
from app.services.slot_generator import generate_slots_for_date
from app.services.request_classifier import classify_requested_time
from datetime import datetime, date
from dateutil import parser as date_parser

router = APIRouter()

@router.post("/twilio-webhook")
async def receive_sms(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    session = get_session()
    print(f"📬 Incoming message from {From} to {To}: {Body}")

    from_phone = normalize_phone(From)
    to_phone = normalize_phone(To)

    owner = session.query(Owner).filter(Owner.twilio_phone_number == to_phone).first()

    if not owner:
        print("⚠️ No owner found for this Twilio number.")
        return Response(status_code=200)

    # ✅ Owner messages
    if from_phone == normalize_phone(owner.personal_phone_number):
        print("📬 Owner message received")
        parsed = parse_owner_message(Body)
        print(f"Owner parsed intent: {parsed}")
        return Response(status_code=200)

    # ✅ Client logic
    client = session.query(Client).filter(Client.phone == from_phone, Client.owner_id == owner.id).first()
    if not client:
        client = Client(owner_id=owner.id, name="Unknown", phone=from_phone)
        session.add(client)
        session.commit()

    parsed = parse_message(Body)
    print(f"AI parsed intent: {parsed}")

    state = session.query(ConversationState).filter(
        ConversationState.client_phone == from_phone, ConversationState.owner_id == owner.id
    ).first()

    if not state:
        state = ConversationState(client_phone=from_phone, owner_id=owner.id, last_updated=datetime.utcnow())
        session.add(state)
        session.commit()

    updated = False

    if parsed.get("client_name") and not state.client_name:
        state.client_name = parsed["client_name"]
        client.name = parsed["client_name"]
        updated = True

    if parsed.get("appointment_datetime") and not (state.appointment_date and state.appointment_time):
        try:
            dt = date_parser.parse(parsed["appointment_datetime"])
            state.appointment_date = dt.date()
            state.appointment_time = dt.time()

            # ⚠️ This is where we run our classifier logic
            classification = classify_requested_time(dt)

            if classification == "after-hours":
                send_sms(from_phone, 
                    "Thanks for your request! This time falls after normal hours. We’ll check with your barber and follow up.")
                return Response(status_code=200)

            elif classification == "pre-hours":
                send_sms(from_phone, 
                    "Thanks for your request! This time is before normal hours. We’ll check availability and follow up.")
                return Response(status_code=200)

            else:
                updated = True

        except Exception as e:
            print(f"⚠️ Failed to parse datetime: {e}")

    state.last_updated = datetime.utcnow()

    if updated:
        session.add(state)
        session.add(client)
        session.commit()

    # ✅ Check if fully ready to book
    missing_fields = []
    if not state.client_name:
        missing_fields.append("name")
    if not (state.appointment_date and state.appointment_time):
        missing_fields.append("appointment date & time")

    if not missing_fields:
        appointment_datetime = datetime.combine(state.appointment_date, state.appointment_time)
        appointment = Appointment(client_id=client.id, appointment_datetime=appointment_datetime, service_type=None)
        session.add(appointment)

        client_phone = state.client_phone
        session.delete(state)
        session.commit()

        send_sms(
            client_phone,
            "✅ Great! Your appointment request has been received. We'll be in touch soon."
        )
        send_sms(
            owner.personal_phone_number,
            f"New appointment request: {client.name} on {appointment_datetime.strftime('%Y-%m-%d %I:%M %p')}"
        )
        return Response(status_code=200)

    else:
        prompt = f"Got it! May I also have: {', '.join(missing_fields)}?"
        send_sms(client.phone, prompt)
        return Response(status_code=200)
