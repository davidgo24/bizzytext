import sys
import requests
import os
from dotenv import load_dotenv

# Load env vars so we can grab LOCAL_WEBHOOK_URL
load_dotenv()

# Your local webhook endpoint
URL = os.getenv("LOCAL_WEBHOOK_URL", "http://localhost:8000/twilio-webhook")

# Parse args
if len(sys.argv) != 3:
    print("Usage: python simulate.py {client|owner} 'message'")
    sys.exit(1)

who = sys.argv[1]
message = sys.argv[2]

# 👇 Sync with your real DB records:
OWNER_PHONE = "+16264665679"  # ✅ Your real personal_phone_number from DB
CLIENT_PHONE = "+15551234567"  # ✅ Use this for client test

# Define test numbers
if who == "owner":
    from_number = OWNER_PHONE
elif who == "client":
    from_number = CLIENT_PHONE
else:
    print("Invalid role. Use 'client' or 'owner'")
    sys.exit(1)

# Always use your actual Twilio business number:
TO_NUMBER = "+16265482282"  # ✅ Your real Twilio business number

# Simulate webhook POST
data = {
    "From": from_number,
    "To": TO_NUMBER,
    "Body": message
}

resp = requests.post(URL, data=data)

print(f"✅ Status: {resp.status_code}")
print(resp.text)
