from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PKT = ZoneInfo("Asia/Karachi")


def format_relative_time(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(PKT)
    now = datetime.now(PKT)
    seconds = int((now - dt).total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        mins = seconds // 60
        return f"{mins}m ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    days = seconds // 86400
    if days < 7:
        return f"{days}d ago"
    return dt.strftime("%d %b")
