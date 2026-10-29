from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.q06_interop import default_backlog_kit, run


BACKLOG_KIT = default_backlog_kit()


@unittest.skipIf(BACKLOG_KIT is None, "Agentic Backlog Kit not found; set AGENTIC_BACKLOG_KIT to run Q06")
class BacklogInteropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cls.result = run(BACKLOG_KIT, Path(temporary))
        cls.checks = {check["id"]: check for check in cls.result["checks"]}

    def assertHeld(self, check_id: str) -> None:
        check = self.checks[check_id]
        self.assertTrue(check["held"], f"{check_id}: {check['observed']}")

    def test_confirmed_finding_exports_and_ingests_as_a_linked_bug(self) -> None:
        self.assertHeld("I1-export-confirmed")
        self.assertHeld("I5-ingest-links-evidence")

    def test_candidates_and_missing_inputs_are_refused(self) -> None:
        self.assertHeld("I2-reject-candidate")
        self.assertHeld("I3-no-guessed-inputs")

    def test_backlog_kit_owns_the_workflow_status(self) -> None:
        self.assertHeld("I4-status-from-backlog-workflow")

    def test_handoff_leaves_the_qa_ledger_alone(self) -> None:
        self.assertHeld("I6-qa-ledger-untouched")

    def test_the_same_finding_is_not_ingested_twice(self) -> None:
        self.assertHeld("I7-no-duplicate-ingest")

    def test_run_never_reaches_github(self) -> None:
        self.assertNotIn("snapshot", self.result["backlog_commands"])
        self.assertNotIn("sync-apply", self.result["backlog_commands"])


if __name__ == "__main__":
    unittest.main()
