from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from agentic_qa_kit.cli import main
from agentic_qa_kit.model import ValidationError, obligation_coverage
from agentic_qa_kit.store import KitStore

from tests.helpers import attempt_input, session_input


def _obligations() -> list[dict]:
    return [
        {
            "id": "ob-half-up",
            "technique": "boundary",
            "source": "README: totals round half up to the cent",
            "statement": "10.005 sits on the rounding boundary",
            "oracle": "Decimal ROUND_HALF_UP gives 10.01",
        },
        {
            "id": "ob-negative",
            "technique": "partition",
            "source": "README: refunds are negative totals",
            "statement": "a negative total is a valid partition",
            "oracle": "-10.005 rounds to -10.01",
        },
        {
            "id": "ob-zero",
            "technique": "boundary",
            "source": "README: zero totals are allowed",
            "statement": "0.000 is the lower boundary of the zero partition",
            "oracle": "0.000 rounds to 0.00",
        },
    ]


class ObligationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = self.temporary.name
        self.store = KitStore(self.root)
        self.store.initialize()
        session = session_input()
        session["charters"][0]["obligations"] = _obligations()
        self.store.create_session(session)

    def test_coverage_separates_exercised_inconclusive_and_unexercised(self) -> None:
        self.store.add_attempt("qa-example", {**attempt_input(), "obligation_ids": ["ob-half-up"]})
        self.store.add_attempt(
            "qa-example",
            {**attempt_input(), "id": "attempt-neg", "outcome": "inconclusive", "obligation_ids": ["ob-negative"]},
        )
        coverage = obligation_coverage(self.store.load_session("qa-example"))
        self.assertEqual(coverage, {"total": 3, "exercised": 1, "inconclusive": 1, "unexercised": 1})

    def test_attempt_may_not_name_an_obligation_its_charter_lacks(self) -> None:
        with self.assertRaisesRegex(ValidationError, "names obligations not in charter"):
            self.store.add_attempt("qa-example", {**attempt_input(), "obligation_ids": ["ob-invented"]})

    def test_obligation_shape_is_checked(self) -> None:
        session = session_input()
        session["id"] = "qa-bad"
        session["charters"][0]["obligations"] = [{**_obligations()[0], "technique": "vibes"}]
        with self.assertRaisesRegex(ValidationError, "technique"):
            self.store.create_session(session)
        session["charters"][0]["obligations"] = [_obligations()[0], _obligations()[0]]
        with self.assertRaisesRegex(ValidationError, "must be unique"):
            self.store.create_session(session)

    def test_summary_reports_obligation_coverage(self) -> None:
        out = StringIO()
        with redirect_stdout(out):
            main(["summary", "--root", self.root])
        summary = json.loads(out.getvalue())["sessions"][0]
        self.assertEqual(summary["obligations"], {"total": 3, "exercised": 0, "inconclusive": 0, "unexercised": 3})

    def test_sessions_without_obligations_still_validate(self) -> None:
        other = KitStore(Path(self.root))
        other.create_session({**session_input(), "id": "qa-plain"})
        self.assertEqual(obligation_coverage(other.load_session("qa-plain"))["total"], 0)


class ExampleTests(unittest.TestCase):
    def test_examples_show_an_obligation_ledger(self) -> None:
        # Agents copy these payloads, so they must carry the design fields.
        examples = Path(__file__).resolve().parents[1] / "examples"
        session = json.loads((examples / "session.json").read_text(encoding="utf-8"))
        attempt = json.loads((examples / "attempt.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            store = KitStore(temporary)
            store.initialize()
            store.create_session(session)
            store.add_attempt(session["id"], attempt)
            coverage = obligation_coverage(store.load_session(session["id"]))
        self.assertEqual(coverage["total"], 2)
        self.assertEqual(coverage["exercised"], 1)


if __name__ == "__main__":
    unittest.main()
