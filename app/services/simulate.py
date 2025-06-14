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
        client_phone = normalize_phone("+6265555555")

        # 🧠 Check for client (create if missing)
        client = session.query(Client).filter(Client.phone == client_phone).first()
        if not client:
            client = Client(name="Sim User", phone=client_phone, owner_id=owner.id)
            session.add(client)
            session.commit()
            print("👤 Created new simulated client.")

        # 🧠 Check for state (create if missing)
        state = session.query(ConversationState).filter(
            ConversationState.client_phone == client.phone,
            ConversationState.owner_id == owner.id
        ).first()
        if not state:
            state = ConversationState(
                client_phone=client.phone,
                owner_id=owner.id,
                client_name=client.name,
                booking_complete=False
            )
            session.add(state)
            session.commit()
            print("🧠 Created new conversation state.")

        parsed = parse_client_message(message)
        print(f"📨 Simulated incoming: \"{message}\"")

        handle_client_message(session, owner, client, state, message, parsed)
