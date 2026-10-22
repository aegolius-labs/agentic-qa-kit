import unittest
from datetime import datetime, timedelta

from worker.expire import HOLD_WINDOW, expired


class ExpireTests(unittest.TestCase):
    def test_expires_old_unpaid_holds(self):
        now = datetime(2026, 1, 1, 12, 0)
        holds = [
            {"id": "old", "created_at": now - HOLD_WINDOW - timedelta(minutes=1)},
            {"id": "paid", "created_at": now - timedelta(hours=1), "paid": True},
            {"id": "new", "created_at": now},
        ]
        self.assertEqual(expired(holds, now), ["old"])


if __name__ == "__main__":
    unittest.main()
