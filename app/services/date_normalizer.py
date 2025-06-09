# app/services/date_normalizer.py

import datetime
import dateparser

def normalize_requested_datetime(raw_text: str, reference_dt: datetime.datetime = None) -> datetime.datetime:
    """
    Parse client's requested date and time into full datetime.
    Uses dateparser for natural language understanding.
    
    :param raw_text: Client message text, e.g. "Friday at 2pm"
    :param reference_dt: (optional) Reference point, defaults to now()
    :return: datetime.datetime object
    """
    if reference_dt is None:
        reference_dt = datetime.datetime.now()

    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': reference_dt,
        'PREFER_DAY_OF_MONTH': 'current',
    }

    parsed = dateparser.parse(raw_text, settings=settings)

    if parsed is None:
        raise ValueError(f"Could not parse date from input: {raw_text}")

    return parsed
