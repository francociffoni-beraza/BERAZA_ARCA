from __future__ import annotations

from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arca.errors import SoapFaultError
from arca.soap.faults import parse_and_raise_fault


class SoapFaultTests(unittest.TestCase):
    def test_parse_soap_fault_raises(self) -> None:
        xml = """
        <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">
          <soapenv:Body>
            <soapenv:Fault>
              <faultcode>soap:Client</faultcode>
              <faultstring>Error en autenticacion</faultstring>
              <detail>detalle</detail>
            </soapenv:Fault>
          </soapenv:Body>
        </soapenv:Envelope>
        """
        root = ET.fromstring(xml)
        with self.assertRaises(SoapFaultError):
            parse_and_raise_fault(root)


if __name__ == "__main__":
    unittest.main()
