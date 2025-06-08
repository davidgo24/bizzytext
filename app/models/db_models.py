from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date, time

# ✅ Owner Table
class Owner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    twilio_phone_number: str
    personal_phone_number: str

# ✅ Client Table
class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="owner.id")
    name: str
    phone: str
    last_visit: Optional[datetime] = None
    last_no_show: Optional[datetime] = None

# ✅ Appointment Table
class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    appointment_datetime: datetime
    service_type: Optional[str] = None
    reminders_sent: Optional[str] = ""
    status: Optional[str] = "scheduled"

class ConversationState(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_phone: str
    owner_id: int
    client_name: Optional[str]
    appointment_date: Optional[date]  # now native
    appointment_time: Optional[time]  # now native
    last_updated: Optional[datetime]
    booking_complete: bool = Field(default=False)
