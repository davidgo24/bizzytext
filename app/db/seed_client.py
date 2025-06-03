# app/db/seed_client.py

from sqlmodel import Session, SQLModel, create_engine
from app.models.db_models import Client
from dotenv import load_dotenv
import os
from app.utils.phone_utils import normalize_phone

# Load environment
load_dotenv(".env_template")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bizzytext.db")
engine = create_engine(DATABASE_URL)

def seed_client():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        client_name = "Daniel"
        client_phone = "+13234594057"  # Your Daniel test number

        client = Client(
            name=client_name,
            phone=normalize_phone(client_phone),
            owner_id=1  # Luis's ID
        )
        session.add(client)
        session.commit()
        print("✅ Daniel seeded!")

if __name__ == "__main__":
    seed_client()
