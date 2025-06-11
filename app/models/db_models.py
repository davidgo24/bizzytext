from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from sqlmodel import Relationship


# ✅ Owner Table
class Owner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    twilio_phone_number: str
    personal_phone_number: str
    appointments: List["Appointment"] = Relationship(back_populates="owner")

    

# ✅ Client Table
class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="owner.id")
    name: str
    phone: str
    last_visit: Optional[datetime] = None
    last_no_show: Optional[datetime] = None


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    owner_id: int = Field(foreign_key="owner.id")  # ✅ Add this line
    appointment_datetime: datetime
    service_type: Optional[str] = None
    reminders_sent: Optional[str] = ""
    status: Optional[str] = "scheduled"

    owner: Optional["Owner"] = Relationship(back_populates="appointments")


class ConversationState(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_phone: str
    owner_id: int
    client_name: Optional[str]
    appointment_date: Optional[date]  # now native
    appointment_time: Optional[time]  # now native
    last_updated: Optional[datetime]
    booking_complete: bool = Field(default=False)
    offered_slots: Optional[str]  # 👈 ADD THIS LINE


metadata = SQLModel.metadata
