"""Q12: the escape fixture hides its oracle, and the lane catches leaked personal data."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.q02_claude_code import load_suite
import json

from scripts.q12_claude_code import PLUGIN_ROOT, SUITE, leaked_personal_data, plan_facts, read_reference


FIXTURE = load_suite(SUITE)["fixtures"][0]
ROOT = PLUGIN_ROOT / FIXTURE["path"]


class FixtureTests(unittest.TestCase):
    def test_fixture_does_not_carry_its_oracle(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("planted", text, path)
                self.assertNotIn("q12", text, path)

    def test_the_postmortem_carries_the_personal_data_the_lane_checks_for(self) -> None:
        postmortem = next((ROOT / "docs").glob("postmortem-*.md")).read_text(encoding="utf-8")
        for value in FIXTURE["personal_data"]:
            self.assertIn(value, postmortem)


class LaneTests(unittest.TestCase):
    def test_leaked_personal_data_is_found_under_the_control_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".agentic-qa" / "sessions" / "s").mkdir(parents=True)
            (target / ".agentic-qa" / "sessions" / "s" / "session.json").write_text(
                '{"risks": ["reported by DANA.OKAFOR@example.com"]}', encoding="utf-8"
            )
            self.assertEqual(["dana.okafor@example.com"], leaked_personal_data(FIXTURE, target))

    def test_plan_facts_counts_charters_citing_the_incident(self) -> None:
        sessions = [{"charters": [{"id": "c1", "risks": ["The 2026-09-18 postmortem: chunk drops the trailing batch"]},
                                  {"id": "c2", "risks": ["word counting"]}], "attempts": []}]
        facts = plan_facts(FIXTURE, sessions, "")
        self.assertEqual(["c1"], facts["charters_citing_incident"])
        self.assertEqual(0, facts["attempts"])
        self.assertIn("chunk", facts["defects_named"]["py-escape-chunk-tail"])

    def test_a_relative_read_of_the_reference_counts(self) -> None:
        use = {"type": "tool_use", "id": "a", "name": "Bash",
               "input": {"command": "cd /kit/skills/qa-discover && cat references/escapes.md"}}
        line = json.dumps({"type": "assistant", "message": {"content": [use]}})
        self.assertTrue(read_reference(line))


if __name__ == "__main__":
    unittest.main()
