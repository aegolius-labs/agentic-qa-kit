from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.cli import main
from agentic_qa_kit.model import ValidationError
from agentic_qa_kit.receipts import canonical, chain_problems, integrity
from agentic_qa_kit.store import KitStore, atomic_write_json

from tests.helpers import attempt_input, session_input


class ReceiptChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = KitStore(self.root)
        self.store.initialize()
        self.store.create_session(session_input())
        self.store.add_attempt("qa-example", attempt_input())
        self.path = self.store.session_path("qa-example")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _raw(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_raw(self, payload: dict) -> None:
        atomic_write_json(self.path, payload)

    def test_every_accepted_write_appends_one_linked_receipt(self) -> None:
        session = self.store.load_session("qa-example")
        receipts = session["receipts"]
        self.assertEqual([r["op"] for r in receipts], ["session-create", "attempt-add"])
        self.assertEqual([r["seq"] for r in receipts], [1, 2])
        self.assertIsNone(receipts[0]["prev"])
        self.assertEqual(receipts[1]["prev"], receipts[0]["digest"])
        self.assertEqual(receipts[1]["subject"], attempt_input()["id"])
        self.assertEqual(chain_problems(session), [])
        self.assertEqual(integrity(session), "chained")

    def test_rejected_write_appends_no_receipt(self) -> None:
        with self.assertRaises(ValidationError):
            self.store.add_attempt("qa-example", attempt_input())
        self.assertEqual(len(self.store.load_session("qa-example")["receipts"]), 2)

    def test_edit_outside_the_ledger_is_detected(self) -> None:
        payload = self._raw()
        payload["attempts"][0]["observation"] = "rewritten by hand"
        self._write_raw(payload)
        session = self.store.load_session("qa-example")
        self.assertEqual(integrity(session), "broken")
        self.assertIn("differs from the state", " ".join(chain_problems(session)))

    def test_removed_middle_receipt_is_detected(self) -> None:
        self.store.add_attempt("qa-example", {**attempt_input(), "id": "attempt-second"})
        payload = self._raw()
        del payload["receipts"][1]
        self._write_raw(payload)
        problems = chain_problems(self.store.load_session("qa-example"))
        self.assertTrue(any("missing or out of order" in p for p in problems))
        self.assertTrue(any("does not link" in p for p in problems))

    def test_dropped_last_receipt_is_detected(self) -> None:
        payload = self._raw()
        payload["receipts"].pop()
        self._write_raw(payload)
        self.assertEqual(integrity(self.store.load_session("qa-example")), "broken")

    def test_rollback_of_both_content_and_receipt_is_not_detected(self) -> None:
        # The chain carries no secret, so truncating the session back to an
        # earlier sealed state is indistinguishable from that state. The
        # contract says so; this test keeps the claim honest.
        payload = self._raw()
        payload["receipts"].pop()
        payload["attempts"].pop()
        payload["status"] = "planned"
        payload["charters"][0]["status"] = "planned"
        self._write_raw(payload)
        self.assertEqual(integrity(self.store.load_session("qa-example")), "chained")

    def test_altered_receipt_is_detected(self) -> None:
        payload = self._raw()
        payload["receipts"][0]["at"] = "2000-01-01T00:00:00Z"
        self._write_raw(payload)
        problems = chain_problems(self.store.load_session("qa-example"))
        self.assertIn("receipt 1 was altered after it was sealed", problems)

    def test_broken_session_refuses_writes_and_fails_validation(self) -> None:
        payload = self._raw()
        payload["attempts"][0]["outcome"] = "pass"
        self._write_raw(payload)
        with self.assertRaisesRegex(ValidationError, "integrity check"):
            self.store.add_attempt("qa-example", {**attempt_input(), "id": "attempt-later"})
        with self.assertRaisesRegex(ValidationError, "integrity check failed for 1 session"):
            self.store.validate_all()

    def test_canonical_form_ignores_key_order_and_whitespace(self) -> None:
        self.assertEqual(canonical({"b": 1, "a": [1, {"d": 2, "c": "é"}]}), canonical({"a": [1, {"c": "é", "d": 2}], "b": 1}))

    def test_new_sessions_are_chained_whatever_version_the_input_names(self) -> None:
        session = self.store.create_session({**session_input(), "id": "qa-old-input", "schema_version": 1})
        self.assertEqual(session["schema_version"], 2)
        self.assertEqual(integrity(session), "chained")


class MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = KitStore(self.root)
        self.store.initialize()
        self.store.create_session(session_input())
        self.store.add_attempt("qa-example", attempt_input())
        self.path = self.store.session_path("qa-example")
        # Rewrite the session as a schema-version-1 ledger would have left it.
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload["schema_version"] = 1
        del payload["receipts"]
        atomic_write_json(self.path, payload)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_version_1_session_stays_valid_and_unchained(self) -> None:
        session = self.store.load_session("qa-example")
        self.assertEqual(integrity(session), "unchained")
        self.assertEqual(self.store.validate_all()["unchained"], 1)
        # Writes to an unmigrated session still work and add no receipts.
        self.store.add_attempt("qa-example", {**attempt_input(), "id": "attempt-v1"})
        self.assertNotIn("receipts", self.store.load_session("qa-example"))

    def test_version_1_session_may_not_carry_receipts(self) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload["receipts"] = []
        atomic_write_json(self.path, payload)
        with self.assertRaisesRegex(ValidationError, "migrate it"):
            self.store.load_session("qa-example")

    def test_migration_seals_the_session_without_changing_its_content(self) -> None:
        before = self.store.load_session("qa-example")
        migrated = self.store.migrate_session("qa-example")
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual([r["op"] for r in migrated["receipts"]], ["migrate"])
        stripped = {k: v for k, v in migrated.items() if k not in {"receipts", "schema_version"}}
        self.assertEqual(stripped, {k: v for k, v in before.items() if k != "schema_version"})
        self.assertEqual(integrity(self.store.load_session("qa-example")), "chained")
        self.store.add_attempt("qa-example", {**attempt_input(), "id": "attempt-after"})
        self.assertEqual(
            [r["op"] for r in self.store.load_session("qa-example")["receipts"]], ["migrate", "attempt-add"]
        )

    def test_migration_runs_once(self) -> None:
        self.store.migrate_session("qa-example")
        with self.assertRaisesRegex(ValidationError, "already at schema version 2"):
            self.store.migrate_session("qa-example")

    def test_terminal_session_can_be_migrated(self) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        payload.update(
            status="completed",
            closed_at="2026-10-22T00:00:00Z",
            decision={"disposition": "hold", "summary": "s", "limitations": [], "residual_risks": [], "next_actions": []},
        )
        atomic_write_json(self.path, payload)
        self.assertEqual(integrity(self.store.migrate_session("qa-example")), "chained")


class CliIntegrityTests(unittest.TestCase):
    def test_summary_and_show_report_integrity_without_the_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = KitStore(tmp)
            store.initialize()
            store.create_session(session_input())
            from contextlib import redirect_stdout
            from io import StringIO

            out = StringIO()
            with redirect_stdout(out):
                main(["summary", "--root", tmp])
            self.assertEqual(json.loads(out.getvalue())["sessions"][0]["integrity"], "chained")
            out = StringIO()
            with redirect_stdout(out):
                main(["show", "--root", tmp, "qa-example"])
            shown = json.loads(out.getvalue())
            self.assertNotIn("receipts", shown)
            self.assertEqual(shown["integrity"], {"status": "chained", "receipts": 1})


if __name__ == "__main__":
    unittest.main()
