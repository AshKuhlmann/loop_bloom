import os
from datetime import datetime


def get_current_datetime() -> datetime:
    """Return the current datetime allowing override via env var."""
    debug_date_str = os.environ.get("LOOPBLOOM_DEBUG_DATE")
    if debug_date_str:
        try:
            return datetime.strptime(debug_date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.now()
    return datetime.now()
