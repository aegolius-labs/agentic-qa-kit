import unittest
from decimal import Decimal

from invoicing import total


class TotalTests(unittest.TestCase):
    def test_rounds_half_up(self) -> None:
        self.assertEqual(Decimal("10.01"), total([("10.005", 1)]))


if __name__ == "__main__":
    unittest.main()
