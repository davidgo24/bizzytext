from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

#owner table

class Owner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    twilio_phone_number: str
    personal_phone_number: Optional[str] = None  # <-- ✅ ADD THIS

    clients: List["Client"] = Relationship(back_populates="owner")

#client 

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="owner.id") #is this foreign bc this client is connected to the owner?
    name: str
    phone: str

    owner: Owner = Relationship(back_populates="clients")
    appointments: List["Appointment"] = Relationship(back_populates="client")

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    appointment_datetime: datetime
    service_type: Optional[str] = None

    client: Client = Relationship(back_populates="appointments")

