# app/services/simulate.py

import sys
from app.db.database import get_session
from app.models.db_models import Owner, Client, ConversationState
from app.services.ai_parser import parse_message, parse_owner_message
from app.services.client_conversation import handle_client_message
from app.services.owner_conversation import handle_owner_message
from app.utils.phone_utils import normalize_phone

session = get_session()

if len(sys.argv) < 3:
    print("Usage: simulate.py [client|owner] [message]")
    sys.exit(1)

who = sys.argv[1]
message = sys.argv[2]

owner = session.query(Owner).first()

if who == "owner":
    print("OWNER MESSAGE:")
    parsed = parse_owner_message(message)
    handle_owner_message(session, owner, parsed)

elif who == "client":
    print("CLIENT MESSAGE:")
    client_phone = "16265554444"  # Fake client test number
    client = session.query(Client).filter(Client.phone == client_phone).first()

    if not client:
        client = Client(owner_id=owner.id, name="Unknown", phone=client_phone)
        session.add(client)
        session.commit()

    state = session.query(ConversationState).filter(
        ConversationState.client_phone == client_phone,
        ConversationState.owner_id == owner.id
    ).first()

    if not state:
        state = ConversationState(client_phone=client_phone, owner_id=owner.id)
        session.add(state)
        session.commit()

    parsed = parse_message(message)
    handle_client_message(session, owner, client, state, message, parsed)

else:
    print("Invalid argument.")
