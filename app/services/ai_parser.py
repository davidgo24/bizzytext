import os
import re
import json
from openai import OpenAI
from app.utils.json_utils import safe_json_parse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_message(message: str) -> dict:
    system_prompt = """
You are BizzyText's AI assistant. Extract booking intent from client texts.

Return strict JSON like:
{
  "intent": "book_appointment",
  "client_name": "...",
  "appointment_datetime": "...",
  "service_type": "..."
}

If you cannot extract something, set it to null. Only output valid JSON. Do NOT explain.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=0.0
    )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw_output)
    except Exception as e:
        print(f"⚠️ Failed to parse JSON from OpenAI: {e}")
        print(f"⚠️ Raw output was: {raw_output}")
        parsed = {
            "intent": "general",
            "client_name": None,
            "appointment_datetime": None,
            "service_type": None
        }
    return parsed

# --- Owner Message Parser ---
def parse_owner_message(message: str) -> dict:
    system_prompt = """
You are BizzyText's assistant helping service business owners log appointment statuses.

Your job is to classify the owner's message into one of these intents:

- confirm_attendance
- mark_no_show
- client_late
- cancel_appointment
- reschedule_appointment
- general

Extract appointment_datetime only if applicable (for reschedule_appointment).

Return your response as strict JSON in this format:

{
  "intent": "...",
  "appointment_datetime": null
}

If no date or time is mentioned, appointment_datetime should be null.
Only output valid JSON — do not include any text or explanation.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=0.0
    )

    raw_output = response.choices[0].message.content.strip()

    # CLEANER PATCH START 🚀
    cleaned_output = re.sub(r"```json|```", "", raw_output).strip()
    try:
        parsed = json.loads(cleaned_output)
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse JSON from OpenAI: {raw_output}")
        parsed = {"intent": "general", "appointment_datetime": None}
    return parsed