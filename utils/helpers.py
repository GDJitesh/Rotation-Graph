# trading_ai_env/utils/helpers.py

from datetime import datetime

def epoch_to_utc(epoch_val):
    """Convert epoch to readable UTC datetime string."""
    return datetime.utcfromtimestamp(epoch_val).strftime('%Y-%m-%d %H:%M:%S')

def epoch_to_date(epoch_val):
    return datetime.utcfromtimestamp(epoch_val).date()
