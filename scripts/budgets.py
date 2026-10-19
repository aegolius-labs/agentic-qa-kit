"""Check the byte budgets that bound what an agent loads and reads (M7).

Model context is the scarce resource a QA run spends. Two things decide how
much of it the kit consumes: the skill text a host loads when a skill
activates, and the ledger output an agent reads back to resume or report. Both
are bounded here, in bytes, because bytes are deterministic and host-neutral
while tokens depend on the model's tokenizer. As a rough guide, English
Markdown and JSON run at three to four bytes per token.

The ledger budgets are measured on a deliberately large synthetic session, so a
summary that grows with the number of attempts fails here rather than in a long
real session. Text the agent writes itself (a discovery profile, a report) is
not engine output and is not budgeted here; the Q01 lane records its size per
observation instead.

Run `python scripts/budgets.py --check` to fail on any exceeded budget.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PLUGIN_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agentic_qa_kit.backlog import build_backlog_item  # noqa: E402
from agentic_qa_kit.cli import _session_summary  # noqa: E402
from agentic_qa_kit.store import KitStore  # noqa: E402


# What one activation loads: the skill body, then its single reference.
SKILL_BODY_BYTES = 3_072
SKILL_REFERENCE_BYTES = 3_072
SKILL_ACTIVATION_BYTES = 5_632
# Every skill's front matter is listed in the host catalog on every turn.
CATALOG_DESCRIPTION_BYTES = 512
# Resume reads `summary`, then targeted `show`; neither may grow with history.
SUMMARY_SESSION_BYTES = 768
SHOW_FINDING_BYTES = 4_096
BACKLOG_PAYLOAD_BYTES = 4_096

SYNTHETIC_ATTEMPTS = 250
SYNTHETIC_FINDINGS = 25


def _json_bytes(payload: Any) -> int:
    return len((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def _front_matter_description(text: str) -> str:
    if not text.startswith("---"):
        return ""
    block = text.split("---", 2)[1]
    for line in block.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


def skill_measurements(root: Path) -> list[dict[str, Any]]:
    rows = []
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        body = skill.read_bytes()
        references = sorted((skill.parent / "references").glob("*.md"))
        largest = max((ref.stat().st_size for ref in references), default=0)
        rows.append(
            {
                "skill": skill.parent.name,
                "body_bytes": len(body),
                "largest_reference_bytes": largest,
                "activation_bytes": len(body) + sum(ref.stat().st_size for ref in references),
                "description_bytes": len(
                    _front_matter_description(body.decode("utf-8")).encode("utf-8")
                ),
            }
        )
    return rows


def _synthetic_session(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    store = KitStore(root)
    store.initialize()
    store.create_session(
        {
            "id": "budget",
            "objective": "Measure ledger output size on a long session",
            "mode": "exploratory",
            "target": {"root": ".", "revision": "0" * 40, "dirty": False, "runtime": ["Python"]},
            "scope": {"include": ["src"], "exclude": ["production"]},
            "context": {
                "intended_use": "Budget measurement",
                "risk_tier": "medium",
                "quality_attributes": ["functional-suitability"],
                "constraints": ["Synthetic"],
                "authorization_notes": ["Local writes are authorized"],
            },
            "charters": [
                {
                    "id": "charter-budget",
                    "title": "Long session",
                    "objective": "Accumulate attempts and findings",
                    "risks": ["Unbounded resume cost"],
                    "quality_attributes": ["functional-suitability"],
                    "methods": ["exploratory"],
                    "oracle": "Independent expected value",
                    "budget": {"minutes": 60, "attempts": SYNTHETIC_ATTEMPTS},
                    "stop_conditions": ["Budget exhausted"],
                    "status": "planned",
                }
            ],
        }
    )
    for index in range(SYNTHETIC_ATTEMPTS):
        store.add_attempt(
            "budget",
            {
                "id": f"attempt-{index:04d}",
                "charter_id": "charter-budget",
                "started_at": "2026-10-15T12:00:00Z",
                "duration_seconds": 1,
                "action": f"Evaluate input {index} against the oracle",
                "environment": {"python": "3.11"},
                "outcome": "fail" if index % 10 == 0 else "pass",
                "exit_code": 1 if index % 10 == 0 else 0,
                "observation": "Observed value recorded",
                "oracle": "Independent expected value",
                "evidence": [{"kind": "test-output", "location": f"evidence/{index:04d}.txt"}],
            },
        )
    for index in range(SYNTHETIC_FINDINGS):
        store.add_finding(
            "budget",
            {
                "id": f"F-{index:03d}",
                "recorded_at": "2026-10-15T12:30:00Z",
                "title": "Synthetic boundary failure",
                "quality_attribute": "functional-suitability",
                "severity": "medium",
                "confidence": "high",
                "status": "confirmed",
                "summary": "The observed value contradicts the independent oracle.",
                "expected": "The oracle value.",
                "actual": "A different value.",
                "oracle": "Independent expected value.",
                "reproduction": {
                    "preconditions": ["Synthetic input"],
                    "steps": ["Run the input", "Compare with the oracle"],
                    "reproducibility": "always",
                    "attempts": 1,
                },
                "attempt_ids": [f"attempt-{index * 10:04d}"],
                "evidence": [{"kind": "test-output", "location": f"evidence/{index * 10:04d}.txt"}],
                "limitations": ["Synthetic session"],
                "acceptance_criteria": ["The oracle value is produced"],
                "suspected_root_cause": "unknown",
            },
        )
    session = store.load_session("budget")
    return session, session["findings"][-1]


def ledger_measurements() -> dict[str, int]:
    with tempfile.TemporaryDirectory() as directory:
        session, finding = _synthetic_session(Path(directory))
        payload = build_backlog_item(
            session,
            finding,
            {
                "parent": None,
                "depends_on": [],
                "impact": 3,
                "effort": 2,
                "business_value": 3,
                "enabler_value": 1,
                "status": "Ready",
                "maturity": "ready",
                "sprint": None,
            },
        )
        return {
            "summary_session_bytes": _json_bytes(_session_summary(session)),
            "show_finding_bytes": _json_bytes(finding),
            "backlog_payload_bytes": _json_bytes(payload),
            "full_session_bytes": _json_bytes(session),
        }


def check(root: Path = PLUGIN_ROOT) -> dict[str, Any]:
    failures: list[str] = []
    skills = skill_measurements(root)
    for row in skills:
        for key, limit in (
            ("body_bytes", SKILL_BODY_BYTES),
            ("largest_reference_bytes", SKILL_REFERENCE_BYTES),
            ("activation_bytes", SKILL_ACTIVATION_BYTES),
            ("description_bytes", CATALOG_DESCRIPTION_BYTES),
        ):
            if row[key] > limit:
                failures.append(f"{row['skill']} {key}={row[key]} exceeds {limit}")
    ledger = ledger_measurements()
    for key, limit in (
        ("summary_session_bytes", SUMMARY_SESSION_BYTES),
        ("show_finding_bytes", SHOW_FINDING_BYTES),
        ("backlog_payload_bytes", BACKLOG_PAYLOAD_BYTES),
    ):
        if ledger[key] > limit:
            failures.append(f"{key}={ledger[key]} exceeds {limit}")
    return {
        "synthetic_session": {"attempts": SYNTHETIC_ATTEMPTS, "findings": SYNTHETIC_FINDINGS},
        "skills": skills,
        "ledger": ledger,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report or check the kit's byte budgets")
    parser.add_argument("--check", action="store_true", help="Exit nonzero when a budget is exceeded")
    args = parser.parse_args(argv)
    report = check()
    print(json.dumps(report, indent=2))
    return 1 if args.check and report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
