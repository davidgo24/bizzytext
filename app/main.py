from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.services import twilio_webhook


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(twilio_webhook.router)


