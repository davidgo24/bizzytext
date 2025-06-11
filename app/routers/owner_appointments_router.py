from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.models.db_models import Appointment, Client
from app.utils.token_utils import get_owner_by_token
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/owner-appointments", response_class=HTMLResponse)
def view_appointments(token: str, request: Request, session: Session = Depends(get_session)):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    appointments = (
        session.query(Appointment, Client)
        .join(Client, Appointment.client_id == Client.id)
        .filter(Client.owner_id == owner.id)
        .filter(Appointment.appointment_datetime >= datetime.now())
        .order_by(Appointment.appointment_datetime)
        .all()
    )

    return templates.TemplateResponse("owner_appointments.html", {
        "request": request,
        "appointments": appointments,
        "owner_name": owner.name
    })
