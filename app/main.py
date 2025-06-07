from fastapi import FastAPI
from app.db.database import engine
from app.services import twilio_webhook
from app.models import db_models


app = FastAPI()

@app.on_event("startup")
def on_startup():
    db_models.SQLModel.metadata.create_all(engine)

app.include_router(twilio_webhook.router)