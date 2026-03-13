from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arca.cache.ta_cache import TaCache
from arca.models.auth import TicketAcceso


class TaCacheTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = TaCache(Path(tmp))
            ticket = TicketAcceso(
                token="token",
                sign="sign",
                generation_time=datetime.now(tz=timezone.utc),
                expiration_time=datetime.now(tz=timezone.utc) + timedelta(hours=1),
                service="wscpe",
            )
            cache.save(ticket, environment="testing", cuit_auth=20000000001)
            loaded = cache.load(environment="testing", service="wscpe", cuit_auth=20000000001)

            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.token, "token")
            self.assertEqual(loaded.sign, "sign")
            self.assertEqual(loaded.service, "wscpe")


if __name__ == "__main__":
    unittest.main()
