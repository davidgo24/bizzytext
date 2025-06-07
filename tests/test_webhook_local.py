import requests

# Change this if your local FastAPI server is running somewhere else
WEBHOOK_URL = "http://localhost:8000/twilio-webhook"

def test_client_text():
    data = {
        "From": "+13234594057",  # pretend this is the client texting
        "To": "+16265482282",    # your Twilio number
        "Body": "Hey can I book an appointment for Wednesday at 12pm?"
    }
    response = requests.post(WEBHOOK_URL, data=data)
    print("Client response:", response.status_code)

# Simulate incoming SMS from the owner
def test_owner_text():
    data = {
        "From": "+16264665679",  # your owner personal phone
        "To": "+16265482282",
        "Body": "List all appointments"
    }
    response = requests.post(WEBHOOK_URL, data=data)
    print("Owner response:", response.status_code)

if __name__ == "__main__":
    test_client_text()
    test_owner_text()
