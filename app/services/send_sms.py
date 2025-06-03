from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv(".env_template")

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def send_sms(to_number: str, message: str):
    message = client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to_number
    )
    print(f"✅ Sent message SID: {message.sid}")
