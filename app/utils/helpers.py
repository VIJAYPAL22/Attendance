# app/utils/helpers.py
from datetime import datetime
import pytz

def current_ist_time():
    """Returns the current time in IST timezone with seconds and microseconds set to 0."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).replace(second=0, microsecond=0)
