from fastapi import APIRouter, Request, Form, Response
from datetime import datetime
from app.db.database import get_session
from app.models.db_models import Owner, Client, ConversationState
from app.services.ai_parser import parse_message, parse_owner_message
from app.services.client_conversation import handle_client_message
from app.services.owner_conversation import handle_owner_message
from app.utils.phone_utils import normalize_phone

router = APIRouter()

@router.post("/twilio-webhook")
async def receive_sms(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    session = get_session()

    from_phone = normalize_phone(From)
    to_phone = normalize_phone(To)

    owner = session.query(Owner).filter(
        Owner.twilio_phone_number == to_phone
    ).first()

    if not owner:
        return Response(status_code=200)

    if from_phone == normalize_phone(owner.personal_phone_number):
        parsed = parse_owner_message(Body)
        handle_owner_message(session, owner, parsed)
        return Response(status_code=200)

    client = session.query(Client).filter(
        Client.phone == from_phone,
        Client.owner_id == owner.id
    ).first()

    if not client:
        client = Client(
            owner_id=owner.id,
            name="Unknown",
            phone=from_phone
        )
        session.add(client)
        session.commit()

    state = session.query(ConversationState).filter(
        ConversationState.client_phone == from_phone,
        ConversationState.owner_id == owner.id
    ).first()

    if not state:
        state = ConversationState(
            client_phone=from_phone,
            owner_id=owner.id,
            last_updated=datetime.utcnow()
        )
        session.add(state)
        session.commit()

    parsed = parse_message(Body)
    handle_client_message(session, owner, client, state, Body, parsed)

    return Response(status_code=200)



'''from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import PlainTextResponse
from app.db.database import get_session
from app.models.db_models import Owner, Client, Appointment, ConversationState
from app.services.ai_parser import parse_message, parse_owner_message
from app.services.client_conversation import handle_client_message
from app.utils.phone_utils import normalize_phone
from app.services.send_sms import send_sms
from app.services.slot_generator import generate_slots_for_date
from datetime import datetime, date, time
from dateutil import parser as date_parser

router = APIRouter()

@router.post("/twilio-webhook")
async def receive_sms(request: Request, Body: str = Form(...), From: str = Form(...), To: str = Form(...)):
    session = get_session()
    print(f"📬 Incoming message from {From} to {To}: {Body}")

    from_phone = normalize_phone(From)
    to_phone = normalize_phone(To)

    owner = session.query(Owner).filter(Owner.twilio_phone_number == to_phone).first()

    if not owner:
        print("⚠️ No owner found for this Twilio number.")
        return Response(status_code=200)

    if from_phone == normalize_phone(owner.personal_phone_number):
        print("📬 Owner message received")
        parsed = parse_owner_message(Body)
        print(f"Owner parsed intent: {parsed}")
        return Response(status_code=200)

    # Client logic starts here
    client = session.query(Client).filter(Client.phone == from_phone, Client.owner_id == owner.id).first()

    if not client:
        client = Client(owner_id=owner.id, name="Unknown", phone=from_phone)
        session.add(client)
        session.commit()
        print(f"✅ New client registered: {client.phone}")

    parsed = parse_message(Body)
    print(f"AI parsed intent: {parsed}")

    
    # Inside your webhook AFTER you detect client logic:
    handle_client_message(owner, client, Body)

    # Load or create state
    state = session.query(ConversationState).filter(
        ConversationState.client_phone == from_phone,
        ConversationState.owner_id == owner.id
    ).first()

    if not state:
        state = ConversationState(
            client_phone=from_phone,
            owner_id=owner.id,
            last_updated=datetime.utcnow()
        )
        session.add(state)
        session.commit()

    updated = False

    # Apply parsed fields
    if parsed.get("client_name") and not state.client_name:
        state.client_name = parsed["client_name"]
        client.name = parsed["client_name"]
        updated = True

    if parsed.get("appointment_datetime") and not (state.appointment_date and state.appointment_time):
        try:
            dt = date_parser.parse(parsed["appointment_datetime"])
            state.appointment_date = dt.date()
            state.appointment_time = dt.time()
            updated = True
        except Exception as e:
            print(f"⚠️ Failed to parse datetime: {e}")

    state.last_updated = datetime.utcnow()
    if updated:
        session.add(state)
        session.add(client)
        session.commit()

    ### 🔥 NEW FLOW: If we don’t have appointment date yet, offer slots
    if not state.appointment_date:
        today = datetime.utcnow().date()
        slots = generate_slots_for_date(today)  # Generate today's availability
        slot_text = ", ".join(slots[:3])  # Send 3 options
        response = f"Got it! I have {slot_text} open today. Reply with a time or check the full calendar: [link]"
        send_sms(client.phone, response)
        return Response(status_code=200)

    ### ✅ Booking complete
    appointment_datetime = datetime.combine(state.appointment_date, state.appointment_time)
    appointment = Appointment(client_id=client.id, appointment_datetime=appointment_datetime)
    session.add(appointment)
    client_phone = state.client_phone
    session.delete(state)
    session.commit()

    send_sms(client_phone, "✅ Great! Your appointment has been booked. See you soon! If you need to reschedule, just text here.")
    send_sms(owner.personal_phone_number, f"New appointment: {client.name} → {appointment_datetime.strftime('%Y-%m-%d %I:%M %p')}")
    return Response(status_code=200)
'''