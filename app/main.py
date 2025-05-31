from fastapi import FastAPI
from sqlmodel import SQLModel, Session, create_engine
import os

from app.models.db_models import Owner, Client, Appointment

DATABASE_URL = "sqlite:///./bizzytext.db"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "BizzyText SaaS is alive!"}
