"""Seam B contract: what this kit hands to Agentic Backlog Kit.

A confirmed defect leaves this kit as one `Bug` payload that
`agentic-backlog-kit` ingests as a manifest item. The two repositories are
independently installable and must not import each other, so the contract is
pinned by a committed fixture on each side.
`tests/fixtures/abk-bug-payload.json` is a real, unedited `backlog-export`
result, byte-identical to the copy in `agentic-backlog-kit` at
`tests/fixtures/qa-handoff/bug-payload.json`, where a matching test proves the
receiving kit can ingest it.

If this test fails, the seam moved. Fix the exporter or update both fixtures
together and say so in the change; do not quietly relax the assertion.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from agentic_qa_kit.backlog import build_backlog_item
from agentic_qa_kit.model import normalize_session

from tests.helpers import backlog_fields, confirmed_finding, session_input


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "abk-bug-payload.json"

# The receiving kit's manifest item requires exactly these fields. It owns `id`
# and generates one on ingestion, so this kit must not supply it.
ABK_ITEM_FIELDS = {
    "title",
    "type",
    "description",
    "acceptance_criteria",
    "parent",
    "depends_on",
    "impact",
    "effort",
    "business_value",
    "enabler_value",
    "status",
    "maturity",
    "sprint",
    # Optional on the receiving side; this kit always sets it, so a repeated
    # handoff of one finding is refused instead of becoming a second Bug.
    "source",
}
ABK_MATURITY = {"idea", "refined", "ready"}
ABK_TYPES = {"Initiative", "Epic", "Feature", "Story", "Bug", "Task"}


class BacklogHandoffContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.item = build_backlog_item(
            normalize_session(session_input()), confirmed_finding(), backlog_fields()
        )

    def test_export_supplies_exactly_the_receiving_field_set(self) -> None:
        self.assertEqual(ABK_ITEM_FIELDS, set(self.item))

    def test_export_never_assigns_a_backlog_id(self) -> None:
        self.assertNotIn("id", self.item)

    def test_export_names_its_session_and_finding_as_the_source(self) -> None:
        session = normalize_session(session_input())
        finding = confirmed_finding()

        self.assertEqual(
            f"agentic-qa-kit:session={session['id']};finding={finding['id']}",
            self.item["source"],
        )

    def test_export_respects_the_receiving_enumerations(self) -> None:
        self.assertEqual("Bug", self.item["type"])
        self.assertIn(self.item["type"], ABK_TYPES)
        self.assertIn(self.item["maturity"], ABK_MATURITY)

        for field in ("impact", "effort", "business_value"):
            self.assertIn(self.item[field], range(1, 6), field)
        self.assertIn(self.item["enabler_value"], range(0, 6))

        self.assertIsInstance(self.item["acceptance_criteria"], list)
        self.assertIsInstance(self.item["depends_on"], list)
        self.assertTrue(self.item["title"])
        self.assertTrue(self.item["description"])

    def test_export_carries_evidence_traceability(self) -> None:
        description = self.item["description"]

        # Without these the receiving backlog item cannot be traced back to the
        # evidence that justified it, and the projection loses its provenance.
        for marker in (
            "QA session:",
            "QA finding:",
            "Target revision:",
            "Oracle:",
            "Evidence:",
            "Limitations:",
        ):
            self.assertIn(marker, description, marker)

    def test_recorded_fixture_still_matches_the_current_shape(self) -> None:
        recorded = json.loads(FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(
            set(recorded),
            set(self.item),
            "the recorded contract fixture and the current exporter disagree",
        )
        self.assertEqual("Bug", recorded["type"])
        self.assertIn(recorded["maturity"], ABK_MATURITY)
        self.assertNotIn("id", recorded)


if __name__ == "__main__":
    unittest.main()
