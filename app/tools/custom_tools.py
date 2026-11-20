from langchain.tools import tool
from datetime import datetime, timezone

@tool
def get_current_datetime()->str:
    """Return the current UTC date and time."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

CUSTOM_TOOLS = [get_current_datetime]