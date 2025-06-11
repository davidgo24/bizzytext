from sqlalchemy.orm import Session
from app.models.db_models import Owner

# ✅ Hardcoded token → owner map (MVP-safe)
TOKEN_OWNER_MAP = {
    "abc123": 1,  # Melissa
    "bob789": 2   # Another owner if needed
}

def get_owner_by_token(token: str, session: Session):
    owner_id = TOKEN_OWNER_MAP.get(token)
    if not owner_id:
        return None
    return session.query(Owner).filter(Owner.id == owner_id).first()
