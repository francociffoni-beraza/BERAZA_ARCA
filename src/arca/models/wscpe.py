from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WscpeAuth:
    token: str
    sign: str
    cuit_representada: int

    def as_dict(self) -> dict[str, object]:
        return {
            "token": self.token,
            "sign": self.sign,
            "cuitRepresentada": self.cuit_representada,
        }
