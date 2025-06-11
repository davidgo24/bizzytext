from app.db.database import SessionLocal
from app.db.seed_owner_schedule import seed_owner_schedule

session = SessionLocal()

# Provide the known owner_id (you said earlier it's 1)
seed_owner_schedule(session, owner_id=1)