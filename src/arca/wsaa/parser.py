from __future__ import annotations

from datetime import datetime
import xml.etree.ElementTree as ET

from ..errors import WsaaError
from ..models.auth import TicketAcceso



def _find_text(node: ET.Element, local_name: str) -> str | None:
    hit = node.find(f".//{{*}}{local_name}")
    if hit is None or hit.text is None:
        return None
    value = hit.text.strip()
    return value or None



def _parse_datetime(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)



def parse_ta(ta_xml: str, *, service: str) -> TicketAcceso:
    try:
        root = ET.fromstring(ta_xml)
    except ET.ParseError as exc:
        raise WsaaError(f"TA XML parse error: {exc}") from exc

    token = _find_text(root, "token")
    sign = _find_text(root, "sign")
    generation_time = _find_text(root, "generationTime")
    expiration_time = _find_text(root, "expirationTime")

    if not token or not sign or not generation_time or not expiration_time:
        raise WsaaError("TA XML missing token/sign/generationTime/expirationTime")

    return TicketAcceso(
        token=token,
        sign=sign,
        generation_time=_parse_datetime(generation_time),
        expiration_time=_parse_datetime(expiration_time),
        service=service,
    )
