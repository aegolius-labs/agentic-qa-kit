from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts import budgets


class BudgetTests(unittest.TestCase):
    def test_repository_is_within_every_budget(self) -> None:
        report = budgets.check()
        self.assertEqual(report["failures"], [])
        self.assertEqual({row["skill"] for row in report["skills"]}, {p.parent.name for p in (budgets.PLUGIN_ROOT / "skills").glob("*/SKILL.md")})

    def test_resume_output_does_not_grow_with_history(self) -> None:
        ledger = budgets.ledger_measurements()
        self.assertLessEqual(ledger["summary_session_bytes"], budgets.SUMMARY_SESSION_BYTES)
        self.assertGreater(ledger["full_session_bytes"], 20 * ledger["summary_session_bytes"])

    def test_oversized_skill_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(budgets.PLUGIN_ROOT / "skills", root / "skills")
            body = root / "skills" / "qa-report" / "SKILL.md"
            body.write_text(body.read_text(encoding="utf-8") + "x" * budgets.SKILL_BODY_BYTES, encoding="utf-8")
            failures = budgets.check(root)["failures"]
        self.assertTrue(any(f.startswith("qa-report body_bytes") for f in failures), failures)

    def test_activation_counts_the_body_and_one_reference(self) -> None:
        # A skill may carry several technique packs; one activation reads one.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(budgets.PLUGIN_ROOT / "skills", root / "skills")
            references = root / "skills" / "qa-session" / "references"
            (references / "extra-pack.md").write_text("x" * 1_000, encoding="utf-8")
            row = next(r for r in budgets.skill_measurements(root) if r["skill"] == "qa-session")
            largest = max(ref.stat().st_size for ref in references.glob("*.md"))
            body = (root / "skills" / "qa-session" / "SKILL.md").stat().st_size
        self.assertEqual(row["activation_bytes"], body + largest)


if __name__ == "__main__":
    unittest.main()
