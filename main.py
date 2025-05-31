from fastapi import FastAPI
from pydantic import BaseModel
from services.conversation_agent import parse_owner_message

app = FastAPI()

class InboundMessage(BaseModel):
    From: str
    Body: str

@app.post("/simulate-inbound")
async def simulate_inbound(payload: InboundMessage):
    message = payload.Body
    parsed = parse_owner_message(message)
    return parsed
