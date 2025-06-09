from app.models.owner_schedule_block import OwnerScheduleBlock
from datetime import time

def seed_owner_schedule(session, owner_id):
    days = {
        0: [(time(8,0), time(14,30)), (time(17,0), time(18,0))],
        1: [(time(8,0), time(14,30)), (time(17,0), time(20,0))],
        2: [(time(8,0), time(14,30)), (time(17,0), time(20,0))],
        3: [(time(8,0), time(14,30)), (time(17,0), time(20,0))],
        4: [(time(8,0), time(14,30)), (time(17,0), time(20,0))]
    }

    for dow, blocks in days.items():
        for block_start, block_end in blocks:
            schedule = OwnerScheduleBlock(
                owner_id=owner_id,
                day_of_week=dow,
                block_start=block_start,
                block_end=block_end
            )
            session.add(schedule)

    session.commit()
    print("✅ Seeded owner schedule!")
