class ArcaError(Exception):
    """Base exception for ARCA integration."""


class ConfigError(ArcaError):
    """Invalid or missing runtime configuration."""


class WsaaError(ArcaError):
    """WSAA authentication error."""


class SoapTransportError(ArcaError):
    """HTTP/SOAP transport error."""


class SoapFaultError(ArcaError):
    """SOAP fault returned by upstream service."""

    def __init__(self, message: str, *, faultcode: str | None = None, faultstring: str | None = None, detail: str | None = None) -> None:
        super().__init__(message)
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.detail = detail


class WscpeError(ArcaError):
    """WSCPE method-level error."""
