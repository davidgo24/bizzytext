# app/db/seed_appointment.py

from sqlmodel import Session, SQLModel, create_engine, select
from app.models.db_models import Appointment, Client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env_template")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bizzytext.db")
engine = create_engine(DATABASE_URL)

def seed_appointment():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Get Daniel's client ID
        client = session.exec(
            select(Client).where(Client.name == "Daniel")
        ).first()

        if not client:
            print("❌ Client not found. Seed client first.")
            return

        # Create test appointment (adjust date/time as needed)
        appointment = Appointment(
            client_id=client.id,
            appointment_datetime=datetime(2025, 6, 5, 10, 0),  # YYYY, MM, DD, HH, MM
            service_type="haircut"
        )
        session.add(appointment)
        session.commit()
        print("✅ Appointment seeded successfully.")

if __name__ == "__main__":
    seed_appointment()
