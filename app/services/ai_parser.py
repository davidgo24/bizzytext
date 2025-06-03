import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

functions = [
    {
        "name": "create_appointment",
        "description": "Extract appointment request details",
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string"},
                "appointment_datetime": {"type": "string", "format": "date-time"},
                "service_type": {"type": "string"}
            },
            "required": ["client_name", "appointment_datetime"]
        }
    }
]

def parse_owner_message(message: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a scheduling assistant helping extract appointment data."},
            {"role": "user", "content": message}
        ],
        functions=functions,
        function_call={"name": "create_appointment"}
    )

    arguments = response.choices[0].message.function_call.arguments
    data = json.loads(arguments)

    return {
        "client_name": data.get("client_name"),
        "appointment_datetime": data.get("appointment_datetime"),
        "service_type": data.get("service_type")
    }
