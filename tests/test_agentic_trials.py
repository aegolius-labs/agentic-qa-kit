"""Q08: agentic trials are judged per dimension, and a critical breach is never averaged away."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agentic_qa_kit.metrics import MIN_DENOMINATOR, trial_report
from agentic_qa_kit.model import AGENTIC_DIMENSIONS, ValidationError, normalize_attempt, validate_trial

from tests.helpers import attempt_input, session_input

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "scripts" / "qa.py"
EXAMPLE = ROOT / "examples" / "agentic-trial-attempt.json"


def trial(index: int, seed=None, **dimensions) -> dict:
    record = {"index": index, "dimensions": dimensions}
    if seed is not None:
        record["seed"] = seed
    return record


def passing(*names: str) -> dict:
    return {name: {"outcome": "pass"} for name in names}


class ValidateTrialTests(unittest.TestCase):
    def test_the_example_is_a_valid_trial_attempt(self) -> None:
        attempt = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        normalize_attempt(attempt)
        self.assertEqual(set(AGENTIC_DIMENSIONS), set(attempt["trial"]["dimensions"]))
        self.assertTrue(attempt["trial"]["dimensions"]["confidentiality"]["critical"])

    def test_an_attempt_without_a_trial_is_unchanged(self) -> None:
        self.assertNotIn("trial", normalize_attempt(attempt_input()))

    def test_a_trial_needs_a_positive_index_and_one_judged_dimension(self) -> None:
        with self.assertRaises(ValidationError):
            validate_trial(trial(0, **passing("utility")))
        with self.assertRaisesRegex(ValidationError, "at least one dimension"):
            validate_trial(trial(1))
        validate_trial(trial(1, seed="s-1", **passing("utility")))
        validate_trial(trial(1, seed=7, **passing("cost")))

    def test_unknown_dimensions_outcomes_and_fields_are_rejected(self) -> None:
        cases = [
            trial(1, quality={"outcome": "pass"}),
            trial(1, utility={"outcome": "partial"}),
            trial(1, utility={"outcome": "pass", "score": 0.9}),
            {"index": 1, "dimensions": passing("utility"), "composite": 0.8},
            trial(1, seed=1.5, **passing("utility")),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValidationError):
                validate_trial(case)

    def test_critical_applies_only_to_a_fail(self) -> None:
        validate_trial(trial(1, safety={"outcome": "fail", "critical": True}))
        for outcome in ("pass", "inconclusive"):
            with self.subTest(outcome=outcome), self.assertRaisesRegex(ValidationError, "only to a fail"):
                validate_trial(trial(1, safety={"outcome": outcome, "critical": True}))
        with self.assertRaises(ValidationError):
            validate_trial(trial(1, safety={"outcome": "fail", "critical": "yes"}))

    def test_attempt_validation_checks_the_trial(self) -> None:
        attempt = attempt_input()
        attempt["trial"] = trial(1, utility={"outcome": "pass", "critical": True})
        with self.assertRaises(ValidationError):
            normalize_attempt(attempt)


def agentic_session(trials: list[dict], charter_id: str = "charter-calculation") -> dict:
    attempts = []
    for record in trials:
        attempt = attempt_input()
        attempt.update(id=f"attempt-{charter_id}-{record['index']}", charter_id=charter_id, trial=record)
        attempts.append(attempt)
    return {"id": "qa-agent", "attempts": attempts}


class TrialReportTests(unittest.TestCase):
    def test_one_critical_breach_fails_its_dimension_at_a_high_pass_rate(self) -> None:
        trials = [trial(i, seed=i, **passing(*AGENTIC_DIMENSIONS)) for i in range(1, 10)]
        trials[2]["dimensions"]["confidentiality"] = {"outcome": "fail", "critical": True}
        report = trial_report(agentic_session(trials))["charters"]["charter-calculation"]
        self.assertEqual((9, 9), (report["trials"], report["distinct_seeds"]))
        confidentiality = report["dimensions"]["confidentiality"]
        self.assertEqual(8 / 9, confidentiality["pass_rate"]["numerator"] / confidentiality["pass_rate"]["denominator"])
        self.assertEqual("critical-breach", confidentiality["verdict"])
        self.assertEqual([{"attempt": "attempt-charter-calculation-3", "trial": 3}], confidentiality["critical_breaches"])
        for name in AGENTIC_DIMENSIONS:
            if name != "confidentiality":
                self.assertEqual("measured", report["dimensions"][name]["verdict"], name)
                self.assertEqual(1.0, report["dimensions"][name]["pass_rate"]["value"])

    def test_there_is_no_composite_score(self) -> None:
        trials = [trial(i, **passing(*AGENTIC_DIMENSIONS)) for i in range(1, 6)]
        result = trial_report(agentic_session(trials))
        charter = result["charters"]["charter-calculation"]
        self.assertEqual({"trials", "distinct_seeds", "dimensions"}, set(charter))
        self.assertTrue(any("composite" in line for line in result["guardrails"]))

    def test_inconclusive_is_excluded_from_the_denominator_and_small_samples_are_withheld(self) -> None:
        trials = [trial(i, recovery={"outcome": "pass"}) for i in range(1, MIN_DENOMINATOR)]
        trials += [trial(i, recovery={"outcome": "inconclusive"}) for i in range(MIN_DENOMINATOR, 9)]
        recovery = trial_report(agentic_session(trials))["charters"]["charter-calculation"]["dimensions"]["recovery"]
        self.assertEqual(MIN_DENOMINATOR - 1, recovery["judged"])
        self.assertEqual(9 - MIN_DENOMINATOR, recovery["inconclusive"])
        self.assertIsNone(recovery["pass_rate"]["value"])
        self.assertIn("withheld", recovery["pass_rate"])

    def test_dimensions_never_judged_are_reported_as_not_measured(self) -> None:
        report = trial_report(agentic_session([trial(1, **passing("utility"))]))
        dimensions = report["charters"]["charter-calculation"]["dimensions"]
        self.assertEqual(list(AGENTIC_DIMENSIONS), list(dimensions))
        self.assertEqual({"judged": 0, "verdict": "not-measured"}, dimensions["cost"])

    def test_attempts_without_a_trial_are_ignored(self) -> None:
        session = agentic_session([trial(1, **passing("utility"))])
        session["attempts"].append(attempt_input())
        self.assertEqual(1, trial_report(session)["charters"]["charter-calculation"]["trials"])

    def test_charters_are_reported_separately(self) -> None:
        session = agentic_session([trial(1, **passing("utility"))], "charter-a")
        session["attempts"] += agentic_session([trial(1, utility={"outcome": "fail"})], "charter-b")["attempts"]
        charters = trial_report(session)["charters"]
        self.assertEqual(["charter-a", "charter-b"], list(charters))
        self.assertEqual(1, charters["charter-b"]["dimensions"]["utility"]["fail"])


class TrialsCliTests(unittest.TestCase):
    def run_qa(self, root: Path, *args: str, payload: dict | None = None) -> dict:
        if payload is not None:
            source = root.parent / "input.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            args = (*args, "--input", str(source))
        result = subprocess.run(
            [sys.executable, str(QA), *args, "--root", str(root)], capture_output=True, text=True, check=False
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_trials_command_reports_a_recorded_breach(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "target"
            root.mkdir()
            self.run_qa(root, "init")
            self.run_qa(root, "session-create", payload=session_input())
            for index in range(1, 6):
                attempt = attempt_input()
                dimensions = passing("utility", "confidentiality")
                if index == 4:
                    dimensions["confidentiality"] = {"outcome": "fail", "critical": True}
                attempt.update(id=f"attempt-{index}", trial=trial(index, seed=index, **dimensions))
                self.run_qa(root, "attempt-add", "qa-example", payload=attempt)
            report = self.run_qa(root, "trials", "qa-example")
        confidentiality = report["charters"]["charter-calculation"]["dimensions"]["confidentiality"]
        self.assertEqual("critical-breach", confidentiality["verdict"])
        self.assertEqual(0.8, confidentiality["pass_rate"]["value"])


if __name__ == "__main__":
    unittest.main()
