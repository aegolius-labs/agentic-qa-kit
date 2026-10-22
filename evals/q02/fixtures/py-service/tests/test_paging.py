import unittest

from app import paging


class PagingTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(paging.parse({}), (1, 20))

    def test_size_is_capped(self):
        self.assertEqual(paging.parse({"size": ["500"]}), (1, 100))

    def test_first_page_starts_at_zero(self):
        self.assertEqual(paging.window(1, 20), (20, 0))


if __name__ == "__main__":
    unittest.main()
