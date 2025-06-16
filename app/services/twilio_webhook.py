from fastapi import APIRouter, Request, Form, Response
from datetime import datetime
from app.db.database import get_session
from app.models.db_models import Owner, Client, ConversationState
from app.services.ai_parser import parse_client_message, parse_owner_message
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

    print("✅ /twilio-webhook POST received from:", from_phone, "| Body:", Body)

    owner = session.query(Owner).filter(
        Owner.twilio_phone_number == to_phone
    ).first()

    if not owner:
        print("❌ No owner matched for Twilio number:", to_phone)
        return Response(status_code=200)

    print("🧑 Owner matched:", owner)

    print("📞 Comparing from_phone vs owner.personal_phone_number...")
    print("FROM:", from_phone)
    print("OWNER PERSONAL:", normalize_phone(owner.personal_phone_number))

    # OWNER messages
    if from_phone == normalize_phone(owner.personal_phone_number):
        print("📨 Incoming message is from OWNER")
        parsed = parse_owner_message(Body)
        handle_owner_message(session, owner, parsed)
        return Response(status_code=200)

    # CLIENT messages
    print("📨 Incoming message is from CLIENT")

    print("🛠 About to parse client message...")
    parsed = parse_client_message(Body)
    print("🛠 Returned from client parser.")
    print("🧠 Parsed message:", parsed)

    client = session.query(Client).filter(
        Client.phone == from_phone,
        Client.owner_id == owner.id
    ).first()

    if not client:
        print("🆕 Creating new client record...")
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
        print("🧠 No state, creating new one...")
        state = ConversationState(
            client_phone=from_phone,
            owner_id=owner.id,
            last_updated=datetime.utcnow(),
            booking_complete=False,
            offered_slots=None
        )
        session.add(state)
        session.commit()

    print("📬 Calling handle_client_message...")
    handle_client_message(session, owner, client, state, Body, parsed)

    return Response(status_code=200)
