from sqlmodel import Session
from app.models.db_models import ConversationState
from datetime import date, time
from typing import Optional


class ConversationStateManager:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_state(
        self,
        client_phone: str,
        owner_id: int,
        client_name: str,
        appointment_date: date,
        appointment_time: time,
        booking_complete: Optional[bool] = None,
    ):
        state = self.db.query(ConversationState).filter_by(
            client_phone=client_phone,
            owner_id=owner_id
        ).first()

        if state:
            state.client_name = client_name
            state.appointment_date = appointment_date
            state.appointment_time = appointment_time
            if booking_complete is not None:
                state.booking_complete = booking_complete
        else:
            state = ConversationState(
                client_phone=client_phone,
                owner_id=owner_id,
                client_name=client_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                booking_complete=booking_complete or False,
            )
            self.db.add(state)

        self.db.commit()

    def clear_state(self, client_phone: str, owner_id: int):
        state = self.db.query(ConversationState).filter_by(
            client_phone=client_phone,
            owner_id=owner_id
        ).first()
        if state:
            self.db.delete(state)
            self.db.commit()
