from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PLUGIN_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agentic_qa_kit.store import KitStore, atomic_write_json


PROFILE = "q01-evidence"


def stage_fixture(root: Path) -> dict[str, str]:
    root = root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError(f"fixture root must be empty: {root}")
    root.mkdir(parents=True, exist_ok=True)

    store = KitStore(root)
    store.initialize()
    store.create_session(
        {
            "id": "q01-fixture",
            "objective": "Provide deterministic evidence for Q01 report and backlog handoff cases",
            "mode": "regression",
            "target": {
                "root": ".",
                "revision": "q01-fixture-revision",
                "dirty": False,
                "runtime": ["Python fixture"],
            },
            "scope": {"include": ["fixture/calculator"], "exclude": ["production"]},
            "context": {
                "intended_use": "Exercise evidence-consuming plugin workflows",
                "risk_tier": "medium",
                "quality_attributes": ["functional-suitability"],
                "constraints": ["Disposable synthetic fixture only"],
                "authorization_notes": ["Local fixture writes are authorized"],
            },
            "charters": [
                {
                    "id": "charter-rounding",
                    "title": "Rounding boundary",
                    "objective": "Check the declared half-up rounding rule",
                    "risks": ["Incorrect customer-visible total"],
                    "quality_attributes": ["functional-suitability"],
                    "methods": ["boundary analysis"],
                    "oracle": "Independent Decimal ROUND_HALF_UP calculation",
                    "budget": {"minutes": 5, "attempts": 1},
                    "stop_conditions": ["One controlled attempt completes"],
                    "status": "planned",
                }
            ],
        }
    )

    evidence_path = root / ".agentic-qa" / "sessions" / "q01-fixture" / "evidence" / "F-001.txt"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        "Input: 10.005\nExpected: 10.01 using ROUND_HALF_UP\nObserved: 10.00\n",
        encoding="utf-8",
    )
    evidence_location = ".agentic-qa/sessions/q01-fixture/evidence/F-001.txt"
    store.add_attempt(
        "q01-fixture",
        {
            "id": "attempt-f001",
            "charter_id": "charter-rounding",
            "started_at": "2026-09-02T12:00:00Z",
            "duration_seconds": 1,
            "action": "Evaluate synthetic input 10.005 against ROUND_HALF_UP oracle",
            "environment": {"fixture": PROFILE},
            "outcome": "fail",
            "exit_code": 1,
            "observation": "Synthetic implementation produced 10.00",
            "oracle": "Independent Decimal ROUND_HALF_UP calculation produces 10.01",
            "evidence": [{"kind": "test-output", "location": evidence_location}],
        },
    )
    store.add_finding(
        "q01-fixture",
        {
            "id": "F-001",
            "recorded_at": "2026-09-02T12:01:00Z",
            "title": "Half-cent total rounds down instead of half up",
            "quality_attribute": "functional-suitability",
            "severity": "high",
            "confidence": "high",
            "status": "confirmed",
            "summary": "The synthetic calculation contradicts the declared rounding rule.",
            "expected": "10.005 rounds to 10.01 using ROUND_HALF_UP.",
            "actual": "10.005 rounds to 10.00.",
            "oracle": "Independent Decimal quantization using ROUND_HALF_UP.",
            "reproduction": {
                "preconditions": ["Use the synthetic Q01 fixture"],
                "steps": ["Calculate 10.005", "Compare the result with ROUND_HALF_UP"],
                "reproducibility": "always",
                "attempts": 1,
            },
            "attempt_ids": ["attempt-f001"],
            "evidence": [{"kind": "test-output", "location": evidence_location}],
            "limitations": ["Synthetic fixture; no production data or services"],
            "acceptance_criteria": ["10.005 produces 10.01 under ROUND_HALF_UP"],
            "suspected_root_cause": "unknown",
        },
    )
    store.close_session(
        "q01-fixture",
        "completed",
        {
            "disposition": "hold",
            "summary": "The tested boundary violates the declared rule.",
            "limitations": ["Synthetic fixture only"],
            "residual_risks": ["Other rounding boundaries were not exercised"],
            "next_actions": ["Review the evidence or prepare a backlog handoff"],
        },
    )

    planning_path = root / ".agentic-qa" / "q01-planning-fields.json"
    atomic_write_json(
        planning_path,
        {
            "parent": None,
            "depends_on": [],
            "impact": 4,
            "effort": 2,
            "business_value": 4,
            "enabler_value": 1,
            "status": "Ready",
            "maturity": "ready",
            "sprint": None,
        },
    )
    backlog_path = root / ".agentic-backlog" / "manifest.json"
    atomic_write_json(
        backlog_path,
        {
            "schema_version": 1,
            "github": {
                "owner": "example",
                "repository": "q01-disposable",
                "project_number": 1,
                "issue_type_mode": "native_or_label",
            },
            "workflow": {
                "hierarchy": [["Initiative"], ["Epic"], ["Feature"], ["Story", "Bug"], ["Task"]],
                "statuses": ["Inbox", "Refining", "Ready", "Planned", "In Progress", "In Review", "Done", "Blocked"],
                "done_statuses": ["Done"],
                "work_item_types": ["Story", "Bug", "Task"],
                "default_capacity": 12,
                "iteration": {"field": "Sprint", "start_date": "2026-09-07", "duration_days": 14},
            },
            "scoring": {
                "weights": {"impact": 2.0, "business_value": 2.0, "enabler_value": 1.0, "effort": 1.0},
                "dependency_boost": 0.25,
            },
            "items": [],
        },
    )
    snapshot_path = root / ".agentic-backlog" / "snapshot.json"
    atomic_write_json(snapshot_path, {"issues": []})
    return {
        "profile": PROFILE,
        "root": str(root),
        "session_id": "q01-fixture",
        "finding_id": "F-001",
        "planning_fields": str(planning_path),
        "backlog_manifest": str(backlog_path),
        "backlog_snapshot": str(snapshot_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage a disposable Q01 evaluation fixture")
    parser.add_argument("--profile", choices=[PROFILE], default=PROFILE)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(stage_fixture(args.root), indent=2))


if __name__ == "__main__":
    main()
