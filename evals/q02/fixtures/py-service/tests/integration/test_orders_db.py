import os
import unittest

from app import server


@unittest.skipUnless(os.environ.get("DATABASE_URL"), "needs DATABASE_URL")
class OrdersDatabaseTests(unittest.TestCase):
    def test_pages_do_not_overlap(self):
        first = server.fetch_orders(*__import__("app.paging").paging.window(1, 2))
        second = server.fetch_orders(*__import__("app.paging").paging.window(2, 2))
        self.assertFalse({o["id"] for o in first} & {o["id"] for o in second})
