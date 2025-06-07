from app.db.database import get_session
from app.models.db_models import Owner
from app.utils.phone_utils import normalize_phone

def seed_owner():
    session = get_session()

    # Your owner info — update freely if you want to seed more owners later
    owner_data = {
        "name": "David",
        "personal_phone_number": normalize_phone("+16264665679"),  # your personal phone
        "twilio_phone_number": normalize_phone("+16265482282")    # your Twilio number
    }

    # Check if owner already exists by personal phone
    existing_owner = session.query(Owner).filter(
        Owner.personal_phone_number == owner_data["personal_phone_number"]
    ).first()

    if existing_owner:
        print("✅ Owner already exists. Skipping insert.")
        return

    new_owner = Owner(**owner_data)
    session.add(new_owner)
    session.commit()
    print("✅ New owner seeded successfully.")

if __name__ == "__main__":
    seed_owner()
