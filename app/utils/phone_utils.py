import re

def normalize_phone(phone: str) -> str:
    phone = str(phone)
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    elif digits.startswith("+1") and len(digits) == 12:
        return digits
    else:
        raise ValueError(f"Invalid phone format: {phone}")
