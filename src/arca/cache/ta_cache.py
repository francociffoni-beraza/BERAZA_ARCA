from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ..models.auth import TicketAcceso


class TaCache:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _cache_path(self, *, environment: str, service: str, cuit_auth: int) -> Path:
        return self.base_dir / environment / service / f"{cuit_auth}.json"

    def load(self, *, environment: str, service: str, cuit_auth: int) -> TicketAcceso | None:
        path = self._cache_path(environment=environment, service=service, cuit_auth=cuit_auth)
        if not path.exists():
            return None

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return TicketAcceso(
                token=str(payload["token"]),
                sign=str(payload["sign"]),
                generation_time=datetime.fromisoformat(str(payload["generation_time"])),
                expiration_time=datetime.fromisoformat(str(payload["expiration_time"])),
                service=str(payload["service"]),
            )
        except Exception:
            return None

    def save(self, ticket: TicketAcceso, *, environment: str, cuit_auth: int) -> Path:
        path = self._cache_path(environment=environment, service=ticket.service, cuit_auth=cuit_auth)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = asdict(ticket)
        payload["generation_time"] = ticket.generation_time.isoformat()
        payload["expiration_time"] = ticket.expiration_time.isoformat()
        payload["cached_at"] = datetime.now(tz=timezone.utc).isoformat()

        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(path)
        return path

    def invalidate(self, *, environment: str, service: str, cuit_auth: int) -> None:
        path = self._cache_path(environment=environment, service=service, cuit_auth=cuit_auth)
        if path.exists():
            path.unlink()
