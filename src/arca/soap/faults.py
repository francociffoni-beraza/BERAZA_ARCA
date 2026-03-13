from __future__ import annotations

import xml.etree.ElementTree as ET

from ..errors import SoapFaultError
from .xml import find_text



def parse_and_raise_fault(root: ET.Element) -> None:
    fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
    if fault is None:
        fault = root.find(".//{*}Fault")
    if fault is None:
        return

    faultcode = find_text(fault, "faultcode")
    faultstring = find_text(fault, "faultstring")
    detail = find_text(fault, "detail")

    message = "SOAP fault"
    if faultcode or faultstring:
        message = f"SOAP fault {faultcode or '-'}: {faultstring or '-'}"

    raise SoapFaultError(
        message,
        faultcode=faultcode,
        faultstring=faultstring,
        detail=detail,
    )
