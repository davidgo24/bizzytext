import re

def normalize_phone(phone: str) -> str:
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # US number with country code (11 digits, starts with '1')
    if len(digits_only) == 11 and digits_only.startswith("1"):
        return f"+{digits_only}"

    # US number without country code (10 digits)
    if len(digits_only) == 10:
        return f"+1{digits_only}"

    # Anything else is considered invalid
    raise ValueError("Invalid phone number format")
