from datetime import datetime

def format_datetime(dt):
    """Safely format a datetime object to an ISO 8601 string."""
    if isinstance(dt, datetime):
        return dt.isoformat()  # Standard ISO format
    return str(dt)  # Fallback for unexpected types
