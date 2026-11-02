"""Q15: the seeded ledger is valid, chained, and exercises withholding; the lane's facts hold."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.metrics import compute
from agentic_qa_kit.store import KitStore
from scripts.q02_claude_code import load_suite
from scripts.q15_claude_code import PLUGIN_ROOT, SUITE, drop_seed_judgements, report_facts, seed_ledger

SUITE_DATA = load_suite(SUITE)
ROOT = PLUGIN_ROOT / SUITE_DATA["fixture"]["path"]


class SeedTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.target = Path(temporary.name)
        seed_ledger(self.target, SUITE_DATA["seed_sessions"], "abc123")
        self.store = KitStore(self.target)

    def test_the_seeded_ledger_validates_with_every_session_closed_and_chained(self) -> None:
        self.store.validate_all()
        sessions = self.store.list_sessions()
        self.assertEqual(8, len(sessions))
        result = compute(sessions)
        self.assertEqual(8, result["scope"]["sessions_included"])
        self.assertEqual({"broken_integrity": 0, "not_closed": 0}, result["scope"]["excluded"])

    def test_the_small_group_is_withheld_and_the_large_one_is_not(self) -> None:
        groups = compute(self.store.list_sessions())["groups"]
        self.assertIsNone(groups["performance-efficiency"]["rates"]["inconclusive_or_error"]["value"])
        self.assertIsNotNone(groups["functional-suitability"]["rates"]["inconclusive_or_error"]["value"])


class FixtureTests(unittest.TestCase):
    def test_the_rota_names_every_seeded_session(self) -> None:
        rota = (ROOT / "docs" / "qa-rota.md").read_text(encoding="utf-8")
        for spec in SUITE_DATA["seed_sessions"]:
            self.assertIn(spec["id"], rota)
        for person in SUITE_DATA["fixture"]["people"]:
            self.assertIn(person, rota)

    def test_fixture_does_not_carry_its_oracle(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("planted", text, path)
                self.assertNotIn("q15", text, path)


class LaneTests(unittest.TestCase):
    def test_judgements_about_seeded_sessions_are_dropped_and_others_kept(self) -> None:
        mechanical = {"status": "fail", "failures": ["qa-tax-rules records revision 'x', not the target HEAD"],
                      "review": ["attempts with an exit code but no matching command: ['qa-tax-rules/attempt-1']", "other"]}
        dropped = drop_seed_judgements(mechanical, ["qa-tax-rules"])
        self.assertEqual(2, len(dropped))
        self.assertEqual(("review", [], ["other"]), (mechanical["status"], mechanical["failures"], mechanical["review"]))
        only_seed = {"status": "review", "failures": [], "review": ["no matching command: ['qa-tax-rules/attempt-1']"]}
        drop_seed_judgements(only_seed, ["qa-tax-rules"])
        self.assertEqual("mechanical-pass", only_seed["status"])

    def test_report_facts(self) -> None:
        use = {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "python /k/scripts/qa.py metrics --root ."}}
        stdout = json.dumps({"type": "assistant", "message": {"content": [use]}})
        facts = report_facts(SUITE_DATA["fixture"], stdout, [".agentic-qa/x", "src/y"], "Priya ran most; rates withheld")
        self.assertTrue(facts["metrics_run"])
        self.assertEqual([".agentic-qa/x"], facts["ledger_paths_changed"])
        self.assertEqual(["Priya Raman"], facts["people_named"])
        self.assertTrue(facts["withheld_mentioned"])


if __name__ == "__main__":
    unittest.main()
