from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arca.wsaa.tra import build_tra
from arca.wsaa.parser import parse_ta


class WsaaTraTests(unittest.TestCase):
    def test_build_tra_contains_expected_fields(self) -> None:
        now = datetime(2026, 3, 12, 14, 0, 0, tzinfo=timezone.utc)
        xml = build_tra("wscpe", now=now).decode("utf-8")

        self.assertIn("<loginTicketRequest version=\"1.0\">", xml)
        self.assertIn("<service>wscpe</service>", xml)
        self.assertIn("<uniqueId>", xml)
        self.assertIn("<generationTime>", xml)
        self.assertIn("<expirationTime>", xml)

    def test_parse_ta(self) -> None:
        ta_xml = """
        <loginTicketResponse>
          <header>
            <generationTime>2026-03-12T13:00:00+00:00</generationTime>
            <expirationTime>2026-03-12T23:00:00+00:00</expirationTime>
          </header>
          <credentials>
            <token>tok123</token>
            <sign>sig456</sign>
          </credentials>
        </loginTicketResponse>
        """
        ta = parse_ta(ta_xml, service="wscpe")
        self.assertEqual(ta.token, "tok123")
        self.assertEqual(ta.sign, "sig456")
        self.assertEqual(ta.service, "wscpe")
        self.assertEqual(ta.generation_time.isoformat(), "2026-03-12T13:00:00+00:00")
        self.assertEqual(ta.expiration_time.isoformat(), "2026-03-12T23:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
