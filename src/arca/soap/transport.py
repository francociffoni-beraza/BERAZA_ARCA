from __future__ import annotations

import time
import xml.etree.ElementTree as ET

import requests

from ..errors import SoapTransportError
from .envelope import SOAPENV_NS, build_envelope
from .faults import parse_and_raise_fault


class SoapClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: int,
        verify_tls: bool = True,
        retries: int = 1,
        retry_backoff_seconds: float = 0.7,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.verify_tls = verify_tls
        self.retries = max(0, retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.session = session or requests.Session()

    def call(
        self,
        *,
        action: str,
        body_xml: str,
        soap_action: str | None = None,
        namespaces: dict[str, str] | None = None,
    ) -> ET.Element:
        envelope = build_envelope(body_xml=body_xml, namespaces=namespaces)

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
        }
        if soap_action:
            headers["SOAPAction"] = soap_action

        response: requests.Response | None = None
        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            try:
                response = self.session.post(
                    self.base_url,
                    data=envelope.encode("utf-8"),
                    headers=headers,
                    timeout=self.timeout_seconds,
                    verify=self.verify_tls,
                )
            except requests.RequestException as exc:
                if attempt >= attempts:
                    raise SoapTransportError(
                        f"SOAP {action} transport error after {attempt} attempts: {exc}"
                    ) from exc
                time.sleep(self.retry_backoff_seconds * attempt)
                continue

            if response.status_code >= 500 and attempt < attempts:
                time.sleep(self.retry_backoff_seconds * attempt)
                continue
            break

        if response is None:
            raise SoapTransportError(f"SOAP {action}: no response")

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as exc:
            if not response.ok:
                raise SoapTransportError(
                    f"SOAP {action} HTTP {response.status_code}: {response.text[:300]}"
                ) from exc
            raise SoapTransportError(f"SOAP {action} invalid XML response: {exc}") from exc

        parse_and_raise_fault(root)

        if not response.ok:
            raise SoapTransportError(f"SOAP {action} HTTP {response.status_code}: {response.text[:300]}")

        body = root.find(f".//{{{SOAPENV_NS}}}Body")
        if body is None:
            body = root.find(".//{*}Body")
        if body is None:
            raise SoapTransportError(f"SOAP {action}: response has no Body")

        children = list(body)
        if not children:
            raise SoapTransportError(f"SOAP {action}: response Body is empty")
        return children[0]
