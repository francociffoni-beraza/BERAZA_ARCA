from __future__ import annotations

from dataclasses import dataclass

from ..cache.ta_cache import TaCache
from ..config import ArcaSettings
from ..models.auth import TicketAcceso
from .client import WsaaClient
from .parser import parse_ta
from .signer import sign_tra
from .tra import build_tra


@dataclass
class WsaaTokenResult:
    ticket: TicketAcceso
    source: str


class WsaaTokenProvider:
    def __init__(self, settings: ArcaSettings, *, cache: TaCache | None = None) -> None:
        self.settings = settings
        self.cache = cache or TaCache(settings.ta_cache_dir)
        self.client = WsaaClient(
            url=settings.wsaa_url,
            timeout_seconds=settings.timeout_seconds,
            verify_tls=settings.verify_tls,
        )

    def get_ta(self, service: str, *, force_refresh: bool = False) -> WsaaTokenResult:
        cached = None if force_refresh else self.cache.load(
            environment=self.settings.environment,
            service=service,
            cuit_auth=self.settings.cuit_auth,
        )

        if cached and not cached.is_expired(skew_seconds=120):
            return WsaaTokenResult(ticket=cached, source="cache")

        tra_xml = build_tra(service)
        cms_b64 = sign_tra(tra_xml, self.settings.cert_path, self.settings.key_path)
        ta_xml = self.client.login_cms(cms_b64)
        ticket = parse_ta(ta_xml, service=service)

        self.cache.save(
            ticket,
            environment=self.settings.environment,
            cuit_auth=self.settings.cuit_auth,
        )
        return WsaaTokenResult(ticket=ticket, source="wsaa")
