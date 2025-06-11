from datetime import datetime, time
from app.models.owner_schedule_block import OwnerScheduleBlock
from app.db.database import get_session

def get_owner_schedule_for_date(owner_id, target_date, session):
    weekday = target_date.weekday()
    return session.query(OwnerScheduleBlock).filter_by(
        owner_id=owner_id,
        day_of_week=weekday
    ).all()

    return blocks  # list of blocks for that date
