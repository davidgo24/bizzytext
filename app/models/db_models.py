from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Owner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    twilio_phone_number: str
    personal_phone_number: str

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int
    name: str
    phone: str


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int
    appointment_datetime: datetime
    service_type: Optional[str] = None
    reminders_sent: Optional[str] = Field(default=None)  # <-- add this line
