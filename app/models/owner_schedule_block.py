from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date, time

class OwnerScheduleBlock(SQLModel, table=True):
    __tablename__ = "owner_schedule_blocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int
    day_of_week: int
    block_start: time
    block_end: time

    class Config:
        arbitrary_types_allowed = True