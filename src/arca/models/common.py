from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SoapCallTrace:
    action: str
    soap_action: str | None
    url: str
    attempt: int
