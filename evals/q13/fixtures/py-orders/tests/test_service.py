import io
import os
import unittest
from unittest import mock

from ordersvc import Metrics, OrderFailed, place_order

CARD = "4111111111111111"


class PlaceOrderTests(unittest.TestCase):
    def test_places_an_order(self) -> None:
        metrics = Metrics()
        with mock.patch.dict(os.environ, {}, clear=False):
            result = place_order("A-1", "BOOK-7", CARD, metrics, log=io.StringIO())
        self.assertEqual("placed", result["status"])
        self.assertEqual(1, metrics.counters["orders_placed_total"])

    def test_out_of_stock_fails_the_order(self) -> None:
        metrics = Metrics()
        with mock.patch.dict(os.environ, {"ORDERSVC_FAKE_INVENTORY": "out_of_stock"}):
            with self.assertRaises(OrderFailed):
                place_order("A-2", "BOOK-7", CARD, metrics, log=io.StringIO())
        self.assertEqual(1, metrics.counters['orders_failed_total{reason="out_of_stock"}'])

    def test_declined_card_fails_the_order(self) -> None:
        with mock.patch.dict(os.environ, {"ORDERSVC_FAKE_PAYMENT": "declined"}):
            with self.assertRaises(OrderFailed):
                place_order("A-3", "BOOK-7", CARD, Metrics(), log=io.StringIO())


if __name__ == "__main__":
    unittest.main()
