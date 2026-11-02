"""Q14: production-mode sessions need a recorded, expiring approval, and the store enforces expiry."""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

from agentic_qa_kit import store as store_module
from agentic_qa_kit.model import PRODUCTION_MODES, SESSION_MODES, ValidationError, normalize_session
from agentic_qa_kit.store import KitStore

from tests.helpers import attempt_input, session_input

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "production-session.json"


def production_session() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def attempt(outcome: str) -> dict:
    return {**attempt_input(), "id": f"attempt-{outcome}", "charter_id": "charter-canary-errors", "outcome": outcome}


class ProductionAuthorizationModelTests(unittest.TestCase):
    def test_production_modes_are_session_modes(self) -> None:
        self.assertTrue(PRODUCTION_MODES <= SESSION_MODES)
        self.assertEqual({"progressive-delivery", "synthetic", "shadow", "field-feedback"}, PRODUCTION_MODES)

    def test_the_example_is_a_valid_production_session(self) -> None:
        normalize_session(production_session())

    def test_every_production_mode_requires_an_approval(self) -> None:
        for mode in PRODUCTION_MODES:
            with self.subTest(mode=mode):
                payload = {**production_session(), "mode": mode}
                del payload["production_authorization"]
                with self.assertRaisesRegex(ValidationError, "requires session.production_authorization"):
                    normalize_session(payload)

    def test_every_field_is_required_and_unknown_fields_are_rejected(self) -> None:
        for field in production_session()["production_authorization"]:
            with self.subTest(field=field):
                payload = production_session()
                del payload["production_authorization"][field]
                with self.assertRaises(ValidationError):
                    normalize_session(payload)
        payload = production_session()
        payload["production_authorization"]["approved_by_agent"] = "yes"
        with self.assertRaisesRegex(ValidationError, "unsupported fields"):
            normalize_session(payload)

    def test_expiry_must_follow_approval_and_carry_a_time_zone(self) -> None:
        payload = production_session()
        payload["production_authorization"]["expires_at"] = "2026-11-02T08:00:00Z"
        with self.assertRaisesRegex(ValidationError, "later than approved_at"):
            normalize_session(payload)
        payload = production_session()
        payload["production_authorization"]["expires_at"] = "2026-11-02T11:00:00"
        with self.assertRaisesRegex(ValidationError, "time zone"):
            normalize_session(payload)

    def test_a_non_production_session_cannot_carry_an_approval(self) -> None:
        payload = deepcopy(session_input())
        payload["production_authorization"] = production_session()["production_authorization"]
        with self.assertRaisesRegex(ValidationError, "only for the production modes"):
            normalize_session(payload)

    def test_an_ordinary_session_gains_no_new_field(self) -> None:
        self.assertNotIn("production_authorization", normalize_session(session_input()))


class ProductionAuthorizationStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = KitStore(Path(temporary.name))
        self.store.initialize()

    def at(self, now: str):
        return mock.patch.object(store_module, "utc_now", return_value=now)

    def test_an_expired_approval_cannot_start_a_session(self) -> None:
        with self.at("2026-11-02T11:00:00Z"), self.assertRaisesRegex(ValidationError, "expires_at has passed"):
            self.store.create_session(production_session())

    def test_after_expiry_only_an_inconclusive_attempt_is_recorded(self) -> None:
        with self.at("2026-11-02T09:30:00Z"):
            self.store.create_session(production_session())
            self.store.add_attempt("qa-canary-checkout", attempt("pass"))
        with self.at("2026-11-02T11:00:01Z"):
            with self.assertRaisesRegex(ValidationError, "production authorization has expired"):
                self.store.add_attempt("qa-canary-checkout", attempt("fail"))
            self.store.add_attempt("qa-canary-checkout", attempt("inconclusive"))
        session = self.store.load_session("qa-canary-checkout")
        self.assertEqual(["pass", "inconclusive"], [a["outcome"] for a in session["attempts"]])
        # The stored session stays valid after its approval lapses.
        self.store.validate_all()


class ProductionModeGuidanceTests(unittest.TestCase):
    def test_qa_session_routes_production_modes_to_session_design(self) -> None:
        skill = Path(__file__).resolve().parents[1] / "skills" / "qa-session"
        self.assertIn("production modes", (skill / "SKILL.md").read_text(encoding="utf-8"))
        design = (skill / "references" / "session-design.md").read_text(encoding="utf-8")
        self.assertIn("## Production modes", design)
        self.assertIn("Never invent an approver", design)
        self.assertIn("Never promote, roll back, or change traffic unless `scope` names it", design)


if __name__ == "__main__":
    unittest.main()
