from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta, date
from app.db.database import get_session
from app.models.owner_schedule_block import OwnerScheduleBlock
from app.models.db_models import Owner
from app.utils.token_utils import get_owner_by_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/owner-availability", response_class=HTMLResponse)
def show_availability(request: Request, token: str, session: Session = Depends(get_session)):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    blocks = session.query(OwnerScheduleBlock).filter_by(owner_id=owner.id).order_by(
        OwnerScheduleBlock.day_of_week, OwnerScheduleBlock.block_start
    ).all()

    return templates.TemplateResponse("owner_availability.html", {
        "request": request,
        "token": token,
        "schedule_blocks": blocks
    })

@router.post("/owner-availability/add", response_class=HTMLResponse)
def add_block(
    request: Request,
    token: str,
    day_of_week: int = Form(...),
    start_hour: int = Form(...),
    start_minute: int = Form(...),
    start_am_pm: str = Form(...),
    end_hour: int = Form(...),
    end_minute: int = Form(...),
    end_am_pm: str = Form(...),
    session: Session = Depends(get_session),
):
    from datetime import time, date, datetime

    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    # Convert to 24-hour time
    if start_am_pm == "PM" and start_hour != 12:
        start_hour += 12
    if start_am_pm == "AM" and start_hour == 12:
        start_hour = 0

    if end_am_pm == "PM" and end_hour != 12:
        end_hour += 12
    if end_am_pm == "AM" and end_hour == 12:
        end_hour = 0

    start = time(start_hour, start_minute)
    end = time(end_hour, end_minute)

    # 🚫 Prevent same-hour blocks
    if start == end:
        blocks = session.query(OwnerScheduleBlock).filter_by(owner_id=owner.id).order_by(
            OwnerScheduleBlock.day_of_week, OwnerScheduleBlock.block_start
        ).all()
        return templates.TemplateResponse("owner_availability.html", {
            "request": request,
            "token": token,
            "schedule_blocks": blocks,
            "error": "Start time and end time cannot be the same."
        })

    block = OwnerScheduleBlock(
        owner_id=owner.id,
        day_of_week=day_of_week,
        block_start=start,
        block_end=end,
    )
    session.add(block)
    session.commit()

    return RedirectResponse(f"/owner-availability?token={token}", status_code=303)

@router.post("/owner-availability/delete", response_class=HTMLResponse)
def delete_block(
    request: Request,
    token: str,
    block_id: int = Form(...),
    session: Session = Depends(get_session)
):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    block = session.query(OwnerScheduleBlock).filter_by(id=block_id, owner_id=owner.id).first()
    if block:
        session.delete(block)
        session.commit()

    return RedirectResponse(f"/owner-availability?token={token}", status_code=303)


def convert_to_24h(hour_str: str, minute_str: str, am_pm: str) -> time:
    hour = int(hour_str)
    minute = int(minute_str)
    if am_pm.upper() == "PM" and hour != 12:
        hour += 12
    if am_pm.upper() == "AM" and hour == 12:
        hour = 0
    return time(hour=hour, minute=minute)