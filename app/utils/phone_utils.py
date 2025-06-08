import re

def normalize_phone(phone):
    if phone.startswith("+"):
        phone = phone[1:]
    return phone.strip()
