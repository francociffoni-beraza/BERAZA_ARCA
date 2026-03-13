from __future__ import annotations

from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape



def build_tra(service: str, now: datetime | None = None, *, ttl_hours: int = 12) -> bytes:
    if now is None:
        now = datetime.now(tz=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    generation = now - timedelta(minutes=5)
    expiration = now + timedelta(hours=ttl_hours)
    unique_id = int(now.timestamp() * 1000)

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<loginTicketRequest version="1.0">'
        "<header>"
        f"<uniqueId>{unique_id}</uniqueId>"
        f"<generationTime>{generation.isoformat(timespec='seconds')}</generationTime>"
        f"<expirationTime>{expiration.isoformat(timespec='seconds')}</expirationTime>"
        "</header>"
        f"<service>{escape(service)}</service>"
        "</loginTicketRequest>"
    )
    return xml.encode("utf-8")
