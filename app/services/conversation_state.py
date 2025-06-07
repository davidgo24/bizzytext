from sqlmodel import Session, select
from app.db.database import get_session
from app.models.db_models import ConversationState
from datetime import datetime

class ConversationStateManager:
    def __init__(self):
        self.session = get_session()

    def get_state(self, client_phone, owner_id):
        stmt = select(ConversationState).where(
            ConversationState.client_phone == client_phone,
            ConversationState.owner_id == owner_id
        )
        result = self.session.exec(stmt).first()
        return result

    def create_or_update_state(self, client_phone, owner_id, client_name=None, appointment_date=None, appointment_time=None):
        state = self.get_state(client_phone, owner_id)

        if state:
            if client_name:
                state.client_name = client_name
            if appointment_date:
                state.appointment_date = appointment_date
            if appointment_time:
                state.appointment_time = appointment_time
            state.last_updated = datetime.now()
            self.session.add(state)
        else:
            state = ConversationState(
                client_phone=client_phone,
                owner_id=owner_id,
                client_name=client_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                last_updated=datetime.now()
            )
            self.session.add(state)

        self.session.commit()
        return state

    def clear_state(self, client_phone, owner_id):
        state = self.get_state(client_phone, owner_id)
        if state:
            self.session.delete(state)
            self.session.commit()
