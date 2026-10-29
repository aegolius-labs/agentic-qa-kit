import unittest

from textstats import chunk, top_words, word_counts


class WordCountTests(unittest.TestCase):
    def test_counts_case_insensitively(self):
        self.assertEqual(word_counts("A a b"), {"a": 2, "b": 1})

    def test_keeps_apostrophes(self):
        self.assertEqual(word_counts("don't stop"), {"don't": 1, "stop": 1})

    def test_top_words_breaks_ties_alphabetically(self):
        self.assertEqual(top_words("b a c a b", 2), [("a", 2), ("b", 2)])


class ChunkTests(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(list(chunk([1, 2, 3, 4], 2)), [[1, 2], [3, 4]])

    def test_rejects_non_positive_size(self):
        with self.assertRaises(ValueError):
            list(chunk([1], 0))


if __name__ == "__main__":
    unittest.main()
