from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.model import ValidationError
from agentic_qa_kit.store import KitStore

from tests.helpers import attempt_input, candidate_finding, decision, session_input


class StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = KitStore(self.root)
        self.store.initialize()
        self.store.create_session(session_input())

    def test_attempt_starts_session_and_preserves_first_record(self) -> None:
        attempt = self.store.add_attempt("qa-example", attempt_input())
        session = self.store.load_session("qa-example")
        self.assertEqual(attempt["id"], "attempt-boundary")
        self.assertEqual(session["status"], "running")
        self.assertEqual(session["attempts"][0]["outcome"], "fail")
        with self.assertRaisesRegex(ValidationError, "attempt already exists"):
            self.store.add_attempt("qa-example", attempt_input())

    def test_candidate_can_transition_to_confirmed(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", candidate_finding())
        updated = self.store.update_finding(
            "qa-example",
            "finding-rounding",
            {
                "status": "confirmed",
                "confidence": "high",
                "reproduction": {
                    "preconditions": ["Default currency configuration"],
                    "steps": ["Calculate 10.005", "Observe the persisted total"],
                    "reproducibility": "once",
                    "attempts": 1,
                },
            },
        )
        self.assertEqual(updated["status"], "confirmed")

    def test_terminal_session_rejects_new_evidence(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        closed = self.store.close_session("qa-example", "completed", decision())
        self.assertEqual(closed["status"], "completed")
        self.assertEqual(closed["charters"][0]["status"], "completed")
        with self.assertRaisesRegex(ValidationError, "terminal session"):
            self.store.add_finding("qa-example", candidate_finding())

    def test_completed_session_blocks_unexecuted_charter(self) -> None:
        closed = self.store.close_session("qa-example", "completed", decision())

        self.assertEqual(closed["status"], "completed")
        self.assertEqual(closed["charters"][0]["status"], "blocked")
        self.assertEqual(closed["attempts"], [])

    def test_completed_session_preserves_partial_execution(self) -> None:
        session = session_input()
        second_charter = dict(session["charters"][0])
        second_charter["id"] = "charter-unexecuted"
        second_charter["title"] = "Unexecuted charter"
        session["charters"].append(second_charter)
        other_root = self.root / "partial"
        other_store = KitStore(other_root)
        other_store.initialize()
        other_store.create_session(session)
        other_store.add_attempt("qa-example", attempt_input())

        closed = other_store.close_session("qa-example", "completed", decision())

        statuses = {charter["id"]: charter["status"] for charter in closed["charters"]}
        self.assertEqual(statuses["charter-calculation"], "completed")
        self.assertEqual(statuses["charter-unexecuted"], "blocked")

    def test_continuation_links_terminal_finding(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", candidate_finding())
        self.store.close_session("qa-example", "completed", decision())
        continuation = session_input()
        continuation["id"] = "qa-continuation"
        continuation["continuation_of"] = {
            "session_id": "qa-example",
            "finding_id": "finding-rounding",
        }

        created = self.store.create_session(continuation)

        self.assertEqual(
            created["continuation_of"],
            {"session_id": "qa-example", "finding_id": "finding-rounding"},
        )
        self.assertEqual(self.store.validate_all()["sessions"], 2)

    def test_continuation_rejects_replacement_source_finding(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", candidate_finding())
        self.store.close_session("qa-example", "completed", decision())
        continuation = session_input()
        continuation["id"] = "qa-continuation"
        continuation["continuation_of"] = {
            "session_id": "qa-example",
            "finding_id": "finding-rounding",
        }
        self.store.create_session(continuation)
        self.store.add_attempt("qa-continuation", attempt_input())

        with self.assertRaisesRegex(ValidationError, "cannot contain a replacement"):
            self.store.add_finding("qa-continuation", candidate_finding())

    def test_continuation_requires_terminal_source(self) -> None:
        continuation = session_input()
        continuation["id"] = "qa-continuation"
        continuation["continuation_of"] = {"session_id": "qa-example"}

        with self.assertRaisesRegex(ValidationError, "source session must be terminal"):
            self.store.create_session(continuation)

    def test_continuation_rejects_unknown_finding(self) -> None:
        self.store.close_session("qa-example", "blocked", decision())
        continuation = session_input()
        continuation["id"] = "qa-continuation"
        continuation["continuation_of"] = {
            "session_id": "qa-example",
            "finding_id": "finding-missing",
        }

        with self.assertRaisesRegex(ValidationError, "unknown finding"):
            self.store.create_session(continuation)

    def test_validate_all_reports_counts(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", candidate_finding())
        self.assertEqual(self.store.validate_all(), {"sessions": 1, "attempts": 1, "findings": 1})


if __name__ == "__main__":
    unittest.main()
