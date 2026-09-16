from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.model import read_json
from agentic_qa_kit.store import KitStore
from scripts.q01_fixture import PROFILE, stage_fixture


class Q01FixtureTests(unittest.TestCase):
    def test_stages_valid_evidence_and_backlog_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "fixture"

            result = stage_fixture(root)

            self.assertEqual(result["profile"], PROFILE)
            self.assertEqual(result["session_id"], "q01-fixture")
            self.assertEqual(result["finding_id"], "F-001")
            self.assertEqual(
                KitStore(root).validate_all(),
                {"sessions": 1, "attempts": 1, "findings": 1},
            )
            session = KitStore(root).load_session("q01-fixture")
            self.assertEqual(session["status"], "completed")
            self.assertEqual(session["charters"][0]["status"], "completed")
            self.assertEqual(session["findings"][0]["status"], "confirmed")
            self.assertTrue((root / session["findings"][0]["evidence"][0]["location"]).is_file())
            self.assertEqual(read_json(root / ".agentic-qa" / "q01-planning-fields.json")["maturity"], "ready")
            backlog = read_json(root / ".agentic-backlog" / "manifest.json")
            self.assertEqual(backlog["items"], [])
            self.assertIn("Bug", backlog["workflow"]["work_item_types"])
            snapshot = read_json(root / ".agentic-backlog" / "snapshot.json")
            self.assertEqual(snapshot, {"issues": []})

    def test_rejects_nonempty_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "existing.txt").write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must be empty"):
                stage_fixture(root)


if __name__ == "__main__":
    unittest.main()
