from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_session
from app.models.db_models import Appointment, Client, Owner
from app.services.slot_generator_v2 import generate_slots_for_date
from app.services.scheduler import book_appointment
from app.utils.token_utils import get_owner_by_token
from app.utils.messaging import notify_bizzy_about_new_web_booking, format_dt_human
from app.services.conversation_state import ConversationStateManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/book/{token}", response_class=HTMLResponse)
def book_page(token: str, request: Request, session: Session = Depends(get_session)):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid booking link."})

    slot_map = {}
    for offset in range(7):
        target_date = datetime.now().date() + timedelta(days=offset)
        slots = generate_slots_for_date(owner.id, target_date, session)
        if slots:
            day_str = target_date.strftime("%A %b %d")
            slot_map[day_str] = slots

    return templates.TemplateResponse("book_appointment.html", {
        "request": request,
        "token": token,
        "slot_map": slot_map
    })

@router.post("/book/{token}", response_class=HTMLResponse)
async def confirm_booking(token: str, request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    slot_time_str = form.get("slot")  # e.g. "Tuesday Jun 18|07:00 PM"
    day_str, time_str = slot_time_str.split("|")

    # Parse to full datetime object (local timezone)
    day_str_full = f"{day_str.strip()} {datetime.now().year}"
    slot_date = datetime.strptime(day_str_full, "%A %b %d %Y").date()
    slot_time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
    slot_dt = datetime.combine(slot_date, slot_time)

    print(f"📆 Final parsed datetime: {slot_dt.isoformat()}")

    # Prevent short-notice bookings
    CUTOFF_MINUTES = 30
    now = datetime.now()
    if slot_dt < (now + timedelta(minutes=CUTOFF_MINUTES)):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "That time slot is no longer available. Please refresh the page and select another time."
        })

    client_name = form.get("name")
    client_phone = form.get("phone")

    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid booking link."})

    # Get or create client
    client = session.query(Client).filter(Client.phone == client_phone).first()
    if not client:
        client = Client(name=client_name, phone=client_phone, owner_id=owner.id)
        session.add(client)
        session.commit()

    # Book appointment
    appointment = book_appointment(session, client, owner.id, slot_dt)

    # Format confirmation slot string
    slot = format_dt_human(slot_dt)

    # Update conversation state
    try:
        ConversationStateManager(db=session).create_or_update_state(
            client_phone=client.phone,
            owner_id=owner.id,
            client_name=client.name,
            appointment_date=slot_dt.date(),
            appointment_time=slot_dt.time(),
            booking_complete=True
        )
    except Exception as e:
        print(f"⚠️ Failed to update ConversationState: {e}")

    # Notify both parties
    notify_bizzy_about_new_web_booking(
        client_name=client.name,
        client_phone=client.phone,
        appointment_datetime=slot_dt,
        owner=owner,
        db=session
    )

    return RedirectResponse(
        url=f"/book/confirmation/{token}?name={client_name}&slot={slot}",
        status_code=303
    )

@router.get("/book/confirmation/{token}", response_class=HTMLResponse)
def confirmation_page(token: str, name: str = "", slot: str = "", request: Request = None):
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "name": name,
        "slot": slot,
        "token": token
    })


