from __future__ import annotations


def session_input() -> dict:
    return {
        "id": "qa-example",
        "objective": "Evaluate the critical calculation path",
        "mode": "functional",
        "target": {
            "root": ".",
            "revision": "abc123",
            "dirty": False,
            "runtime": ["Python 3.11"],
        },
        "scope": {"include": ["src/calculator.py"], "exclude": ["production"]},
        "context": {
            "intended_use": "Calculate customer-visible totals",
            "risk_tier": "high",
            "quality_attributes": ["functional-suitability"],
            "constraints": ["Use generated fixtures only"],
            "authorization_notes": ["Existing local tests are authorized"],
        },
        "charters": [
            {
                "id": "charter-calculation",
                "title": "Calculation boundaries",
                "objective": "Check total calculation around rounding boundaries",
                "risks": ["Incorrect customer-visible total"],
                "quality_attributes": ["functional-suitability"],
                "methods": ["boundary analysis", "focused unit execution"],
                "oracle": "An independently calculated decimal result",
                "budget": {"minutes": 15, "attempts": 4},
                "stop_conditions": ["Budget exhausted", "Target revision changes"],
                "status": "planned",
            }
        ],
    }


def attempt_input() -> dict:
    return {
        "id": "attempt-boundary",
        "charter_id": "charter-calculation",
        "started_at": "2026-08-27T12:00:00Z",
        "duration_seconds": 2,
        "action": "python -m unittest tests.test_calculator",
        "environment": {"python": "3.11", "locale": "C.UTF-8"},
        "outcome": "fail",
        "exit_code": 1,
        "observation": "Total rounded down at the half-cent boundary",
        "oracle": "Expected half-up result from an independent Decimal calculation",
        "evidence": [
            {
                "kind": "test-output",
                "location": ".agentic-qa/sessions/qa-example/evidence/test-output.txt",
            }
        ],
    }


def candidate_finding() -> dict:
    return {
        "id": "finding-rounding",
        "recorded_at": "2026-08-27T12:01:00Z",
        "title": "Half-cent totals round down instead of half up",
        "quality_attribute": "functional-suitability",
        "severity": "high",
        "confidence": "medium",
        "status": "candidate",
        "summary": "A customer-visible total differs from the declared rounding rule.",
        "expected": "10.005 rounds to 10.01 using the declared half-up rule.",
        "actual": "10.005 rounds to 10.00.",
        "oracle": "Independent Decimal quantization using ROUND_HALF_UP.",
        "reproduction": {
            "preconditions": ["Default currency configuration"],
            "steps": ["Calculate a total of 10.005"],
            "reproducibility": "once",
            "attempts": 1,
        },
        "attempt_ids": ["attempt-boundary"],
        "evidence": [
            {
                "kind": "test-output",
                "location": ".agentic-qa/sessions/qa-example/evidence/test-output.txt",
            }
        ],
        "limitations": ["Only one runtime was exercised"],
        "acceptance_criteria": ["10.005 produces 10.01 under the declared currency rounding rule"],
        "suspected_root_cause": "unknown",
    }


def confirmed_finding() -> dict:
    finding = candidate_finding()
    finding["status"] = "confirmed"
    finding["confidence"] = "high"
    finding["reproduction"] = {
        "preconditions": ["Default currency configuration"],
        "steps": ["Calculate a total of 10.005", "Observe the persisted total"],
        "reproducibility": "once",
        "attempts": 1,
    }
    return finding


def backlog_fields() -> dict:
    return {
        "parent": None,
        "depends_on": [],
        "impact": 4,
        "effort": 2,
        "business_value": 4,
        "enabler_value": 1,
        "status": "Backlog",
        "maturity": "ready",
        "sprint": None,
    }


def decision() -> dict:
    return {
        "disposition": "hold",
        "summary": "The tested calculation boundary violates the declared rule.",
        "limitations": ["Only Python 3.11 was exercised"],
        "residual_risks": ["Other rounding boundaries may be affected"],
        "next_actions": ["Hand the confirmed defect to the backlog"],
    }
