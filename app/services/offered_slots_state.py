import json
from datetime import datetime

def save_offered_slots(session, state, slots):
    """
    Store list of slots offered (as ISO strings) into state.
    """
    iso_slots = [dt.isoformat() for dt in slots]
    state.offered_slots = json.dumps(iso_slots)
    session.add(state)
    session.commit()

def get_offered_slots(state):
    """
    Retrieve list of previously offered slots from state.
    """
    if not state.offered_slots:
        return []
    iso_slots = json.loads(state.offered_slots)
    return [datetime.fromisoformat(s) for s in iso_slots]
