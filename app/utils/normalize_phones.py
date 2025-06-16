# scripts/normalize_phones.py

from app.db.database import get_session
from app.models.db_models import Owner, Client
from app.utils.phone_utils import normalize_phone

def normalize_all_phones():
    session = get_session()

    owners = session.query(Owner).all()
    for owner in owners:
        try:
            orig_twilio = owner.twilio_phone_number
            orig_personal = owner.personal_phone_number

            owner.twilio_phone_number = normalize_phone(orig_twilio)
            owner.personal_phone_number = normalize_phone(orig_personal)

            print(f"🔁 Owner {owner.id}: Twilio {orig_twilio} → {owner.twilio_phone_number}, Personal {orig_personal} → {owner.personal_phone_number}")
        except Exception as e:
            print(f"❌ Error normalizing owner {owner.id}: {e}")

    clients = session.query(Client).all()
    for client in clients:
        try:
            orig_phone = client.phone
            client.phone = normalize_phone(orig_phone)
            print(f"🔁 Client {client.id}: {orig_phone} → {client.phone}")
        except Exception as e:
            print(f"❌ Error normalizing client {client.id}: {e}")

    session.commit()
    print("✅ All phone numbers normalized and saved.")

if __name__ == "__main__":
    normalize_all_phones()
