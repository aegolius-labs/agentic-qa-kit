"""Q15: cross-session metrics carry denominators and intervals, withhold small samples, and never group by person."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.metrics import GROUPINGS, MIN_DENOMINATOR, compute, rate, wilson
from agentic_qa_kit.model import ValidationError

QA = Path(__file__).resolve().parents[1] / "scripts" / "qa.py"


def session(sid: str, *, mode="functional", attributes=("functional-suitability",), outcomes=(), findings=(),
            status="completed", tier="medium") -> dict:
    return {
        "schema_version": 1,
        "id": sid,
        "mode": mode,
        "status": status,
        "created_at": f"2026-10-{len(sid):02d}T00:00:00Z",
        "context": {"quality_attributes": list(attributes), "risk_tier": tier},
        "charters": [{"id": "c", "obligations": []}],
        "attempts": [{"id": f"a{i}", "charter_id": "c", "outcome": o} for i, o in enumerate(outcomes)],
        "findings": [{"id": f"f{i}", "status": s} for i, s in enumerate(findings)],
        "production_authorization": {"approver": "A Person"},
    }


class RateTests(unittest.TestCase):
    def test_wilson_interval_matches_a_known_value(self) -> None:
        self.assertEqual([0.2366, 0.7634], wilson(5, 10))
        self.assertEqual([0.0, 0.4345], wilson(0, 5))
        self.assertIsNone(wilson(0, 0))

    def test_small_denominators_are_withheld(self) -> None:
        small = rate(2, MIN_DENOMINATOR - 1)
        self.assertIsNone(small["value"])
        self.assertIsNone(small["interval_95"])
        self.assertIn("withheld", small)
        self.assertEqual((2, MIN_DENOMINATOR - 1), (small["numerator"], small["denominator"]))
        shown = rate(2, 8)
        self.assertEqual(0.25, shown["value"])
        self.assertEqual(2, len(shown["interval_95"]))


class ComputeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sessions = [
            session("s1", outcomes=["pass", "fail", "inconclusive"], findings=["confirmed", "dismissed"]),
            session("s22", attributes=("functional-suitability", "reliability"), outcomes=["pass", "error", "pass"],
                    findings=["confirmed", "candidate"]),
            session("s333", status="running", outcomes=["pass"]),
        ]

    def test_overall_counts_and_rates(self) -> None:
        result = compute(self.sessions)
        overall = result["overall"]
        self.assertEqual(2, result["scope"]["sessions_included"])
        self.assertEqual({"broken_integrity": 0, "not_closed": 1}, result["scope"]["excluded"])
        self.assertEqual(6, overall["attempts"]["total"])
        inconclusive = overall["rates"]["inconclusive_or_error"]
        self.assertEqual((2, 6), (inconclusive["numerator"], inconclusive["denominator"]))
        self.assertAlmostEqual(0.3333, inconclusive["value"])
        confirmed = overall["rates"]["confirmed_of_resolved_findings"]
        self.assertEqual((2, 3), (confirmed["numerator"], confirmed["denominator"]))
        self.assertIsNone(confirmed["value"])

    def test_a_session_counts_once_in_each_of_its_attributes(self) -> None:
        result = compute(self.sessions)
        self.assertTrue(result["scope"]["groups_overlap"])
        self.assertEqual(2, result["groups"]["functional-suitability"]["sessions"])
        self.assertEqual(1, result["groups"]["reliability"]["sessions"])
        self.assertFalse(compute(self.sessions, "mode")["scope"]["groups_overlap"])

    def test_never_groups_by_person_or_reads_the_approver(self) -> None:
        self.assertEqual(("quality-attribute", "mode", "risk-tier"), GROUPINGS)
        for by in ("approver", "person", "agent", "responsible_agent"):
            with self.assertRaisesRegex(ValidationError, "never by person"):
                compute(self.sessions, by)
        self.assertNotIn("A Person", json.dumps(compute(self.sessions)))

    def test_broken_sessions_are_excluded_not_averaged(self) -> None:
        broken = {**session("s4444", outcomes=["pass"] * 9), "schema_version": 2, "receipts": []}
        result = compute([*self.sessions, broken])
        self.assertEqual(1, result["scope"]["excluded"]["broken_integrity"])
        self.assertEqual(6, result["overall"]["attempts"]["total"])

    def test_guardrails_travel_with_the_numbers(self) -> None:
        guardrails = " ".join(compute(self.sessions)["guardrails"])
        for phrase in ("never of people", "withheld", "Wilson", "broken receipt chain", "do not set targets"):
            self.assertIn(phrase, guardrails)


class CliTests(unittest.TestCase):
    def test_help_renders(self) -> None:
        for argv in (["--help"], ["metrics", "--help"]):
            run = subprocess.run([sys.executable, str(QA), *argv], capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)

    def test_metrics_command_on_an_empty_ledger_and_refuses_people(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            subprocess.run([sys.executable, str(QA), "init", "--root", root], check=True, capture_output=True)
            run = subprocess.run([sys.executable, str(QA), "metrics", "--root", root], capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)
            payload = json.loads(run.stdout)
            self.assertEqual(0, payload["scope"]["sessions_included"])
            self.assertIsNone(payload["overall"]["rates"]["inconclusive_or_error"]["value"])
            refused = subprocess.run([sys.executable, str(QA), "metrics", "--root", root, "--by", "person"],
                                     capture_output=True, text=True)
            self.assertNotEqual(0, refused.returncode)


class GuidanceTests(unittest.TestCase):
    def test_qa_report_routes_trends_to_metrics_and_refuses_ranking(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "skills" / "qa-report" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("QA trends across sessions", text.split("---")[1])
        self.assertIn("run `metrics`", text)
        self.assertIn("never rank or compare people or agents, even when asked", text)


if __name__ == "__main__":
    unittest.main()
