from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.models.owner_schedule_block import OwnerScheduleBlock
from app.models.db_models import Owner
from app.utils.token_utils import get_owner_by_token
from datetime import time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/owner-availability", response_class=HTMLResponse)
def show_availability(request: Request, token: str, session: Session = Depends(get_session)):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    schedule_blocks = session.query(OwnerScheduleBlock).filter_by(owner_id=owner.id).order_by(
        OwnerScheduleBlock.day_of_week, OwnerScheduleBlock.block_start
    ).all()

    return templates.TemplateResponse("owner_availability.html", {
        "request": request,
        "token": token,
        "blocks": schedule_blocks
    })

@router.post("/owner-availability", response_class=HTMLResponse)
def update_availability(
    request: Request,
    token: str,
    day_of_week: int = Form(...),
    start_hour: int = Form(...),
    start_minute: int = Form(...),
    end_hour: int = Form(...),
    end_minute: int = Form(...),
    session: Session = Depends(get_session)
):
    owner = get_owner_by_token(token, session)
    if not owner:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Invalid token."})

    new_block = OwnerScheduleBlock(
        owner_id=owner.id,
        day_of_week=day_of_week,
        block_start=time(start_hour, start_minute),
        block_end=time(end_hour, end_minute)
    )
    session.add(new_block)
    session.commit()

    return RedirectResponse(f"/owner-availability?token={token}", status_code=303)
