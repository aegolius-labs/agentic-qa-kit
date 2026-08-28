from __future__ import annotations

import unittest

from agentic_qa_kit.backlog import build_backlog_item
from agentic_qa_kit.model import ValidationError, normalize_session

from tests.helpers import backlog_fields, candidate_finding, confirmed_finding, session_input


class BacklogTests(unittest.TestCase):
    def test_exports_confirmed_finding_as_bug(self) -> None:
        session = normalize_session(session_input())
        item = build_backlog_item(session, confirmed_finding(), backlog_fields())
        self.assertEqual(item["type"], "Bug")
        self.assertEqual(item["impact"], 4)
        self.assertIn("QA finding: `finding-rounding`", item["description"])
        self.assertIn("Target revision: `abc123`", item["description"])

    def test_rejects_candidate_finding(self) -> None:
        session = normalize_session(session_input())
        with self.assertRaisesRegex(ValidationError, "only confirmed"):
            build_backlog_item(session, candidate_finding(), backlog_fields())

    def test_does_not_infer_missing_business_value(self) -> None:
        session = normalize_session(session_input())
        fields = backlog_fields()
        del fields["business_value"]
        with self.assertRaisesRegex(ValidationError, "business_value"):
            build_backlog_item(session, confirmed_finding(), fields)


if __name__ == "__main__":
    unittest.main()
