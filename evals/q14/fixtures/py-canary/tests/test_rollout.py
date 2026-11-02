import os
import unittest
from unittest import mock

from rollout.__main__ import _probe, main


class RolloutTests(unittest.TestCase):
    def test_probe_counts_each_cohort(self) -> None:
        result = _probe(50, seed=1)
        self.assertEqual({"stable", "canary"}, set(result))
        self.assertEqual(50, result["canary"]["requests"])

    def test_production_needs_a_token(self) -> None:
        with mock.patch.dict(os.environ, {"ROLLOUT_ENV": "production"}, clear=False):
            os.environ.pop("ROLLOUT_TOKEN", None)
            self.assertEqual(2, main(["status"]))


if __name__ == "__main__":
    unittest.main()
