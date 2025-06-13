from datetime import datetime
import pytz

def to_utc(pacific_dt: datetime) -> datetime:
    return pacific_dt.astimezone(pytz.utc)
