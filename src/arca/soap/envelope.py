from __future__ import annotations

SOAPENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"



def build_envelope(body_xml: str, namespaces: dict[str, str] | None = None) -> str:
    xmlns = [f'xmlns:soapenv="{SOAPENV_NS}"']
    if namespaces:
        for prefix, uri in namespaces.items():
            xmlns.append(f'xmlns:{prefix}="{uri}"')

    body = body_xml.strip()
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<soapenv:Envelope {' '.join(xmlns)}>"
        "<soapenv:Header/>"
        f"<soapenv:Body>{body}</soapenv:Body>"
        "</soapenv:Envelope>"
    )
