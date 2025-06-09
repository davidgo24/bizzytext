from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv(".env_template")

# Pull from env vars
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

# Determine if we're in LOCAL SMS MODE
LOCAL_SMS = os.getenv("LOCAL_SMS", "false").lower() == "true"

def send_sms(to_phone, body):
    if LOCAL_SMS:
        print(f"[SIMULATED SMS] To: {to_phone} | Body: {body}")
        return

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to_phone
    )
    print(f"✅ Sent message SID: {message.sid}")
