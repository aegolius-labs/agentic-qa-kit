from __future__ import annotations

import unittest

from agentic_qa_kit.model import ValidationError, normalize_finding, normalize_session, validate_manifest
from agentic_qa_kit.store import KitStore

from tests.helpers import confirmed_finding, session_input


class ModelTests(unittest.TestCase):
    def test_normalizes_session_defaults(self) -> None:
        payload = normalize_session(session_input())
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["receipts"], [])
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["attempts"], [])
        self.assertIsNone(payload["decision"])

    def test_rejects_unknown_quality_attribute(self) -> None:
        payload = session_input()
        payload["context"]["quality_attributes"] = ["quality"]
        with self.assertRaisesRegex(ValidationError, "quality_attributes"):
            normalize_session(payload)

    def test_confirmed_finding_requires_evidence(self) -> None:
        payload = confirmed_finding()
        payload["evidence"] = []
        with self.assertRaisesRegex(ValidationError, "requires evidence"):
            normalize_finding(payload)

    def test_finding_reproduction_count_matches_linked_attempts(self) -> None:
        payload = confirmed_finding()
        payload["reproduction"]["attempts"] = 2
        with self.assertRaisesRegex(ValidationError, "number of linked attempt_ids"):
            normalize_finding(payload)

    def test_manifest_authorization_classes_are_disjoint(self) -> None:
        manifest = KitStore(".").default_manifest()
        manifest["authorization"]["forbidden"].append("read_repository")
        with self.assertRaisesRegex(ValidationError, "mutually exclusive"):
            validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
