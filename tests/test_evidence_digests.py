from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.model import ValidationError
from agentic_qa_kit.store import KitStore

from tests.helpers import attempt_input, candidate_finding, session_input

LOCATION = ".agentic-qa/sessions/qa-example/evidence/test-output.txt"


class EvidenceDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.store = KitStore(self.root)
        self.store.initialize()
        self.store.create_session(session_input())
        self.evidence = self.root / LOCATION
        self.evidence.parent.mkdir(parents=True, exist_ok=True)
        self.evidence.write_bytes(b"expected 3, observed 2\n")
        self.expected = "sha256:" + hashlib.sha256(b"expected 3, observed 2\n").hexdigest()

    def _attempt(self, **evidence: str) -> dict:
        return {**attempt_input(), "evidence": [{"kind": "log", "location": LOCATION, **evidence}]}

    def test_write_digests_an_evidence_file_in_the_repository(self) -> None:
        attempt = self.store.add_attempt("qa-example", self._attempt())
        self.assertEqual(attempt["evidence"][0]["digest"], self.expected)
        self.assertEqual(self.store.validate_all()["evidence_verified"], 1)

    def test_changed_evidence_file_fails_validation(self) -> None:
        self.store.add_attempt("qa-example", self._attempt())
        self.evidence.write_bytes(b"expected 3, observed 3\n")
        with self.assertRaisesRegex(ValidationError, "changed after they were recorded"):
            self.store.validate_all()

    def test_missing_evidence_file_is_counted_not_failed(self) -> None:
        self.store.add_attempt("qa-example", self._attempt())
        self.evidence.unlink()
        counts = self.store.validate_all()
        self.assertEqual((counts["evidence_verified"], counts["evidence_missing"]), (0, 1))

    def test_supplied_digest_must_match_the_file(self) -> None:
        with self.assertRaisesRegex(ValidationError, "does not match the file"):
            self.store.add_attempt("qa-example", self._attempt(digest="sha256:" + "0" * 64))
        self.assertEqual(self.store.add_attempt("qa-example", self._attempt(digest=self.expected))["id"], "attempt-boundary")

    def test_locations_outside_the_repository_are_left_alone(self) -> None:
        attempt = {**attempt_input(), "evidence": [
            {"kind": "url", "location": "https://ci.example.invalid/run/1"},
            {"kind": "log", "location": "../outside.log"},
            {"kind": "log", "location": "not-yet-written.log"},
        ]}
        recorded = self.store.add_attempt("qa-example", attempt)
        self.assertTrue(all("digest" not in entry for entry in recorded["evidence"]))

    def test_finding_update_digests_only_new_entries_and_keeps_old_ones(self) -> None:
        self.store.add_attempt("qa-example", attempt_input())
        finding = {**candidate_finding(), "evidence": [{"kind": "log", "location": LOCATION}]}
        self.store.add_finding("qa-example", finding)
        second = self.root / "second.log"
        second.write_bytes(b"second run\n")
        # Restating the first entry without its digest is not a rewrite.
        updated = self.store.update_finding(
            "qa-example",
            finding["id"],
            {"evidence": [{"kind": "log", "location": LOCATION}, {"kind": "log", "location": "second.log"}]},
        )
        self.assertEqual(updated["evidence"][0]["digest"], self.expected)
        self.assertTrue(updated["evidence"][1]["digest"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
