"""Q11: the suite-trust fixture behaves as its oracle says, and the lane names planted causes."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

from scripts.q02_claude_code import load_suite
from scripts.q11_claude_code import PLUGIN_ROOT, SUITE, defects_named


FIXTURE = load_suite(SUITE)["fixtures"][0]
ROOT = PLUGIN_ROOT / FIXTURE["path"]


def _run(*tests: str, hash_seed: str = "0") -> bool:
    env = {**os.environ, "PYTHONPATH": "src", "PYTHONHASHSEED": hash_seed, "PYTHONDONTWRITEBYTECODE": "1"}
    command = [sys.executable, "-m", "unittest", *(tests or ("discover", "-s", "tests"))]
    return subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False).returncode == 0


class FixtureTests(unittest.TestCase):
    def test_fixture_does_not_carry_its_oracle(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("planted", text, path)
                self.assertNotIn("q11", text, path)

    def test_dedupe_verdict_depends_on_the_hash_seed(self) -> None:
        test = "tests.test_core.CoreTests.test_dedupe_keeps_first_occurrence_order"
        verdicts = {_run(test, hash_seed=str(seed)) for seed in range(16)}
        self.assertEqual({True, False}, verdicts)

    def test_default_size_test_passes_only_after_the_configuring_test(self) -> None:
        alone = "tests.test_core.CoreTests.test_batches_with_default_size"
        after = "tests.test_core.CoreTests.test_batches_uses_configured_size"
        self.assertFalse(_run(alone))
        self.assertTrue(_run(after, alone))


class DefectsNamedTests(unittest.TestCase):
    def test_reports_keywords_from_findings_and_answer(self) -> None:
        sessions = [{"findings": [{"title": "dedupe loses first occurrence order", "summary": "varies by PYTHONHASHSEED"}]}]
        named = defects_named(FIXTURE, sessions, "One test fails when run alone.")
        self.assertIn("pythonhashseed", named["py-flaky-dedupe-order"])
        self.assertEqual(["alone"], named["py-flaky-order-dependent-test"])


if __name__ == "__main__":
    unittest.main()
