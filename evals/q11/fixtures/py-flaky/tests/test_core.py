import unittest

from batchtools import batches, configure, dedupe


class CoreTests(unittest.TestCase):
    def test_batches_uses_configured_size(self):
        configure(batch_size=2)
        self.assertEqual(batches([1, 2, 3]), [[1, 2], [3]])

    def test_batches_with_default_size(self):
        self.assertEqual(len(batches(list(range(4)))[0]), 2)

    def test_dedupe_keeps_first_occurrence_order(self):
        self.assertEqual(dedupe(["pear", "apple", "pear"]), ["pear", "apple"])


if __name__ == "__main__":
    unittest.main()
