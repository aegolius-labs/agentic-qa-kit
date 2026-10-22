from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agentic_qa_kit.model import ValidationError
from agentic_qa_kit.store import KitStore

from tests.helpers import attempt_input, candidate_finding, confirmed_finding, decision, session_input

QA = Path(__file__).resolve().parents[1] / "scripts" / "qa.py"


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
        self.assertEqual(
            self.store.validate_all(),
            {"sessions": 1, "chained": 1, "unchained": 0, "attempts": 1, "findings": 1, "evidence_verified": 0, "evidence_missing": 0},
        )


    def test_update_cannot_rewrite_a_confirmed_observation(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", confirmed_finding())
        for field, value in (("actual", "10.005 rounds to 10.01."), ("expected", "Anything.")):
            with self.subTest(field=field), self.assertRaisesRegex(ValidationError, f"finding.{field} is fixed"):
                self.store.update_finding("qa-example", "finding-rounding", {field: value})
        with self.assertRaisesRegex(ValidationError, "recorded_at cannot change"):
            self.store.update_finding("qa-example", "finding-rounding", {"recorded_at": "2026-09-01T00:00:00Z"})
        self.assertEqual(self.store.load_session("qa-example")["findings"][0]["actual"], "10.005 rounds to 10.00.")

    def test_update_cannot_erase_recorded_evidence(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", candidate_finding())
        for field in ("evidence", "limitations"):
            with self.subTest(field=field), self.assertRaisesRegex(ValidationError, f"finding.{field} is append-only"):
                self.store.update_finding("qa-example", "finding-rounding", {field: []})

    def test_every_settled_field_is_fixed_once_confirmed(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", confirmed_finding())
        rewrites = {field: "Rewritten." for field in ("title", "summary", "expected", "actual", "oracle")}
        rewrites["severity"] = "low"
        rewrites["acceptance_criteria"] = ["Any total is accepted"]
        for field, value in rewrites.items():
            with self.subTest(field=field), self.assertRaisesRegex(ValidationError, f"finding.{field} is fixed"):
                self.store.update_finding("qa-example", "finding-rounding", {field: value})
        reproduction = confirmed_finding()["reproduction"]
        for field, value in (
            ("preconditions", ["A different configuration"]),
            ("steps", ["Calculate a total of 10.005"]),
            ("reproducibility", "always"),
        ):
            with self.subTest(field=f"reproduction.{field}"):
                with self.assertRaisesRegex(ValidationError, f"finding.reproduction.{field} is fixed"):
                    self.store.update_finding(
                        "qa-example", "finding-rounding", {"reproduction": dict(reproduction, **{field: value})}
                    )
        stored = self.store.load_session("qa-example")["findings"][0]
        self.assertEqual(stored["severity"], "high")
        self.assertEqual(stored["reproduction"], reproduction)

    def test_confirmed_finding_still_links_new_attempts(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", confirmed_finding())
        later = attempt_input()
        later["id"] = "attempt-later"
        self.store.add_attempt("qa-example", later)
        finding = confirmed_finding()
        updated = self.store.update_finding(
            "qa-example",
            "finding-rounding",
            {
                "attempt_ids": finding["attempt_ids"] + ["attempt-later"],
                "reproduction": dict(finding["reproduction"], attempts=2),
            },
        )
        self.assertEqual(updated["reproduction"]["attempts"], 2)

    def test_every_history_field_rejects_removal_and_rewrite(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        other = attempt_input()
        other["id"] = "attempt-other"
        self.store.add_attempt("qa-example", other)
        self.store.add_finding("qa-example", candidate_finding())
        finding = candidate_finding()
        no_attempts = dict(finding["reproduction"], attempts=0)
        changes = {
            "attempt_ids": (
                {"attempt_ids": [], "reproduction": no_attempts},
                {"attempt_ids": ["attempt-other"]},
            ),
            "evidence": (
                {"evidence": []},
                {"evidence": [{"kind": "log", "location": ".agentic-qa/sessions/qa-example/evidence/other.log"}]},
            ),
            "limitations": ({"limitations": []}, {"limitations": ["A different limitation"]}),
        }
        for field, (removal, rewrite) in changes.items():
            for label, payload in (("removal", removal), ("rewrite", rewrite)):
                with self.subTest(field=field, change=label):
                    with self.assertRaisesRegex(ValidationError, f"finding.{field} is append-only"):
                        self.store.update_finding("qa-example", "finding-rounding", payload)
        stored = self.store.load_session("qa-example")["findings"][0]
        for field in changes:
            self.assertEqual(stored[field], finding[field])

    def test_update_may_append_evidence_and_limitations(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        self.store.add_finding("qa-example", confirmed_finding())
        finding = confirmed_finding()
        extra = {"kind": "log", "location": ".agentic-qa/sessions/qa-example/evidence/extra.log"}
        updated = self.store.update_finding(
            "qa-example",
            "finding-rounding",
            {
                "evidence": finding["evidence"] + [extra],
                "limitations": finding["limitations"] + ["Only one locale was exercised"],
            },
        )
        self.assertEqual(updated["evidence"][-1], extra)
        self.assertEqual(len(updated["limitations"]), 2)

    def test_concurrent_writers_lose_no_records(self) -> None:
        writers = 12
        inputs = []
        for index in range(writers):
            attempt = attempt_input()
            attempt["id"] = f"attempt-parallel-{index:02d}"
            path = self.root / f"attempt-{index}.json"
            path.write_text(json.dumps(attempt), encoding="utf-8")
            inputs.append(path)

        def add(path: Path) -> int:
            command = [sys.executable, str(QA), "attempt-add", "qa-example", "--root", str(self.root), "--input", str(path)]
            return subprocess.run(command, capture_output=True, text=True, check=False).returncode

        with ThreadPoolExecutor(writers) as pool:
            codes = list(pool.map(add, inputs))

        self.assertEqual(codes, [0] * writers)
        stored = {item["id"] for item in self.store.load_session("qa-example")["attempts"]}
        self.assertEqual(stored, {f"attempt-parallel-{index:02d}" for index in range(writers)})


class EvidenceRootTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.store = KitStore(self.root)
        self.store.initialize()

    def _set_evidence_root(self, value: str) -> None:
        manifest = json.loads(self.store.manifest_path.read_text(encoding="utf-8"))
        manifest["defaults"]["evidence_root"] = value
        self.store.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_default_root_keeps_sessions_under_the_control_directory(self) -> None:
        self.store.create_session(session_input())
        self.assertTrue((self.root / ".agentic-qa" / "sessions" / "qa-example" / "session.json").is_file())

    def test_sessions_follow_the_manifest_evidence_root(self) -> None:
        self._set_evidence_root("qa-evidence/sessions")
        self.store.create_session(session_input())
        self.store.add_attempt("qa-example", attempt_input())
        self.assertTrue((self.root / "qa-evidence" / "sessions" / "qa-example" / "session.json").is_file())
        self.assertFalse((self.root / ".agentic-qa" / "sessions").exists())
        self.assertEqual([s["id"] for s in self.store.list_sessions()], ["qa-example"])
        self.assertEqual(self.store.validate_all()["attempts"], 1)

    def test_root_that_escapes_through_a_symlink_is_refused(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        try:
            (self.root / "escape").symlink_to(outside.name, target_is_directory=True)
        except OSError:
            self.skipTest("this host cannot create symlinks")
        self._set_evidence_root("escape")
        with self.assertRaisesRegex(ValidationError, "inside the target repository"):
            self.store.create_session(session_input())


if __name__ == "__main__":
    unittest.main()
