from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TicketAcceso:
    token: str
    sign: str
    generation_time: datetime
    expiration_time: datetime
    service: str

    def is_expired(self, *, skew_seconds: int = 60) -> bool:
        return datetime.now(tz=self.expiration_time.tzinfo) >= (self.expiration_time - timedelta(seconds=skew_seconds))
