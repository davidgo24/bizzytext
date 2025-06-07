import json

def safe_json_parse(raw_output: str):
    if not raw_output or not raw_output.strip():
        print("⚠️ Empty response from OpenAI.")
        return None

    try:
        parsed = json.loads(raw_output)
        return parsed
    except json.JSONDecodeError as e:
        print("⚠️ Failed to parse JSON from OpenAI:", e)
        print("⚠️ Raw output was:", raw_output)
        return None
