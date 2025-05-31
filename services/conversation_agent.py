import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env_template")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_owner_message(message: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Bizzy, an AI-powered scheduling assistant for service business owners. "
                    "The owner will send you casual text messages to schedule appointments for their clients. "
                    "Extract who the appointment is for, when it's scheduled, and propose a confirmation message. "
                    "If information is missing, politely ask follow-up questions. "
                    "Be clear, short, friendly, and easy for the owner to understand."
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    reply = response.choices[0].message.content

    return {
        "status": "received",
        "bizzy_reply": reply
    }
