from twilio.rest import Client
from dotenv import load_dotenv
import os

from app.utils.phone_utils import normalize_phone  # ✅ New import

load_dotenv(".env_template")

# Pull from env vars
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

# Determine if we're in LOCAL SMS MODE
LOCAL_SMS = os.getenv("LOCAL_SMS", "true").lower() == "true"

def send_sms(to_phone, body):
    try:
        normalized = normalize_phone(to_phone)
    except ValueError:
        print(f"⚠️ Skipping SMS – invalid phone number: {to_phone}")
        return

    if LOCAL_SMS:
        print(f"📩 Outbound simulated SMS → To: {normalized} | Body: {body}")
        return

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=normalized
    )
    print(f"✅ Sent message SID: {message.sid}")
