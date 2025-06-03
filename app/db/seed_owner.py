from sqlmodel import Session, SQLModel, create_engine
from app.models.db_models import Owner
from dotenv import load_dotenv
import os
from app.utils.phone_utils import normalize_phone

load_dotenv(".env_template")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bizzytext.db")
engine = create_engine(DATABASE_URL)

def seed_owner():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        owner = Owner(
            name="Luis Aka Boricutz",
            twilio_phone_number=normalize_phone("+16265482282"),  # Twilio number
            personal_phone_number=normalize_phone("+16264665679")  # Owner's personal number (Luis)
        )
        session.add(owner)
        session.commit()

if __name__ == "__main__":
    seed_owner()
