# app/utils/phone_utils.py

def normalize_phone(phone: str) -> str:
    """Remove any non-digit characters (e.g. +, -, spaces, parentheses)"""
    return ''.join(filter(str.isdigit, phone))
