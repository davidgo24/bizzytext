from datetime import datetime, time
from app.models.owner_schedule_block import OwnerScheduleBlock
from app.db.database import get_session

def get_owner_schedule_for_date(owner_id, target_date):
    session = get_session()
    day_of_week = target_date.weekday()  # Monday=0, Sunday=6

    blocks = session.query(OwnerScheduleBlock).filter(
        OwnerScheduleBlock.owner_id == owner_id,
        OwnerScheduleBlock.day_of_week == day_of_week
    ).all()

    return blocks  # list of blocks for that date
