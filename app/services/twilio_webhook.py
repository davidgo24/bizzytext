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

    owner = session.query(Owner).filter(
        Owner.twilio_phone_number == to_phone
    ).first()

    if not owner:
        return Response(status_code=200)

    # Owner messages (internal)
    if from_phone == normalize_phone(owner.personal_phone_number):
        parsed = parse_owner_message(Body)
        handle_owner_message(session, owner, parsed)
        return Response(status_code=200)

    # Client messages (external)
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
            last_updated=datetime.utcnow(),
            booking_complete=False,
            offered_slots=None
        )
        session.add(state)
        session.commit()

    parsed = parse_client_message(Body)
    handle_client_message(session, owner, client, state, Body, parsed)

    return Response(status_code=200)
