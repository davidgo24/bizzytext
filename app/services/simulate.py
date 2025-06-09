# app/services/simulate.py

from app.services.client_conversation import handle_client_message
from app.services.ai_parser import parse_client_message
from app.db.database import SessionLocal
from app.models.db_models import Owner, Client, ConversationState
from app.utils.phone_utils import normalize_phone

import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simulate.py client <message>")
        sys.exit(1)

    entity = sys.argv[1]
    message = sys.argv[2]

    session = SessionLocal()

    if entity == "client":
        owner = session.query(Owner).first()
        client = session.query(Client).filter(Client.phone == normalize_phone("+16265554444")).first()

        state = (
            session.query(ConversationState)
            .filter(ConversationState.client_phone == client.phone, ConversationState.owner_id == owner.id)
            .first()
        )

        parsed = parse_client_message(message)

        # ✅ ADD THIS LINE (log your input)
        print(f"📨 Simulated incoming: \"{message}\"")

        handle_client_message(session, owner, client, state, message, parsed)
