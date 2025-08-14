from datetime import datetime
from flask_babel import format_timedelta

def time_ago(value):
    if value is None:
        return "давно"
    
    now = datetime.utcnow()
    if now >= value:
        diff = now - value
        return format_timedelta(diff, add_direction=False) + " назад"
    else:
        diff = value - now
        return "через " + format_timedelta(diff, add_direction=False)
