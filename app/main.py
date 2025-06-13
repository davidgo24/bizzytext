from fastapi import FastAPI
from app.db.database import engine
from app.services import twilio_webhook
from app.models import db_models
from app.routers import booking_routes
from app.routers import owner_availability_router



app = FastAPI()

@app.on_event("startup")
def on_startup():
    db_models.SQLModel.metadata.create_all(engine)

app.include_router(twilio_webhook.router)
app.include_router(booking_routes.router)
app.include_router(owner_availability_router.router)
    