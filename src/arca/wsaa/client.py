from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from ..errors import WsaaError


WSAA_NS = "http://wsaa.view.sua.dvadac.desein.afip.gov"
SOAPENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"



def _find_text(node: ET.Element, local_name: str) -> str | None:
    hit = node.find(f".//{{*}}{local_name}")
    if hit is None or hit.text is None:
        return None
    value = hit.text.strip()
    return value or None


class WsaaClient:
    def __init__(self, *, url: str, timeout_seconds: int, verify_tls: bool = True, session: requests.Session | None = None) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.verify_tls = verify_tls
        self.session = session or requests.Session()

    def login_cms(self, cms_b64: str) -> str:
        envelope = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            f'<soapenv:Envelope xmlns:soapenv="{SOAPENV_NS}" xmlns:wsaa="{WSAA_NS}">'
            "<soapenv:Header/>"
            "<soapenv:Body>"
            "<wsaa:loginCms>"
            f"<wsaa:in0>{cms_b64}</wsaa:in0>"
            "</wsaa:loginCms>"
            "</soapenv:Body>"
            "</soapenv:Envelope>"
        )

        try:
            response = self.session.post(
                self.url,
                data=envelope.encode("utf-8"),
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": '""',
                },
                timeout=self.timeout_seconds,
                verify=self.verify_tls,
            )
        except requests.RequestException as exc:
            raise WsaaError(f"WSAA transport error: {exc}") from exc

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as exc:
            if not response.ok:
                raise WsaaError(
                    f"WSAA loginCms HTTP {response.status_code}: {response.text[:1000]}"
                ) from exc
            raise WsaaError(f"WSAA XML parse error: {exc}") from exc

        fault = root.find(f".//{{{SOAPENV_NS}}}Fault") or root.find(".//{*}Fault")
        if fault is not None:
            faultcode = _find_text(fault, "faultcode")
            faultstring = _find_text(fault, "faultstring")
            detail = _find_text(fault, "detail")
            raise WsaaError(
                f"WSAA SOAP fault: {faultcode or '-'} {faultstring or '-'} {detail or ''}".strip()
            )

        if not response.ok:
            raise WsaaError(
                f"WSAA loginCms HTTP {response.status_code}: {response.text[:1000]}"
            )

        login_return = _find_text(root, "loginCmsReturn")
        if not login_return:
            raise WsaaError("WSAA response missing loginCmsReturn")

        return login_return
