import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load env vars
load_dotenv(".env_template")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# STRICT system prompt — this is the key upgrade
SYSTEM_PROMPT = """
You are an AI assistant helping a business owner manage client text messages for appointment scheduling.
You must ALWAYS respond in valid JSON. Do not use any extra commentary or explanation.

Your JSON format is:

{
  "intent": "<one of: book_appointment, reschedule, cancel_appointment, general>",
  "client_name": "<client name or null>",
  "appointment_datetime": "<ISO 8601 datetime or null>",
  "service_type": "<service type or null>"
}

Some rules:
- If the intent is general, all other fields must be null.
- Only return valid JSON, no text.
- Always use ISO8601 for datetime: YYYY-MM-DDTHH:MM:SS
- If name is unclear, set client_name to null.
- If time is unclear, set appointment_datetime to null.
- If service is unclear, set service_type to null.
"""

def parse_message(message: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.0
    )

    raw_output = response.choices[0].message.content
    print("🧪 RAW AI OUTPUT:", raw_output)

    try:
        # Clean common formatting quirks
        cleaned_output = raw_output.strip().strip("`").replace("json", "").strip()
        parsed = json.loads(cleaned_output)
    except json.JSONDecodeError as e:
        print("⚠️ JSON parsing failed:", e)
        parsed = {
            "intent": "general",
            "client_name": None,
            "appointment_datetime": None,
            "service_type": None
        }

    return parsed
