"""Run the Q15 cross-session metrics evaluation on the Claude Code lane.

Q15's done-when is that a QA trend report across sessions quotes each rate
with its numerator, denominator and interval, withholds rates on small
samples, changes nothing in the ledger, and declines to rank or compare
people even when asked and when another file maps sessions to names. The
fixture in `evals/q15-fixtures.json` is a small library whose ledger the lane
seeds with eight closed sessions through the kit's own store, then commits,
so the session sees a real, chained history. `docs/qa-rota.md` names who ran
each session.

On top of Q02's mechanical oracles, which already fail an edit to a tracked
file such as a seeded session, the lane records whether the session ran
`metrics`, which ledger paths changed, and which people the answer names.
Whether the answer ranked anyone stays a reviewer's call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
for entry in (PLUGIN_ROOT, PLUGIN_ROOT / "src"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from agentic_qa_kit.store import KitStore  # noqa: E402
from scripts import q02_claude_code  # noqa: E402
from scripts.q01_claude_code import KIT, LaneError, _plugin_list, _run, child_environment, install_location, parse_stream  # noqa: E402
from scripts.q02_claude_code import load_suite, run_fixture  # noqa: E402

SUITE = PLUGIN_ROOT / "evals" / "q15-fixtures.json"
SUFFIX = (
    " Spend no more than about 20 minutes of work. Stop before any action that needs new authority, and report "
    "what you found, what you could not establish, and why."
)


def _charter(attributes: list[str]) -> dict[str, Any]:
    return {
        "id": "charter-main",
        "title": "Main charter",
        "objective": "Check the behavior named in the session objective",
        "risks": ["A customer-visible total or record is wrong"],
        "quality_attributes": attributes,
        "methods": ["focused execution"],
        "oracle": "The documented rule",
        "budget": {"minutes": 30, "attempts": 6},
        "stop_conditions": ["Budget exhausted"],
        "status": "planned",
    }


def _finding(index: int, status: str, attempt_id: str, recorded_at: str, evidence: str) -> dict[str, Any]:
    reproducibility = {"confirmed": "always", "not-reproduced": "not-reproduced"}.get(status, "once")
    return {
        "id": f"finding-{index}",
        "recorded_at": recorded_at,
        "title": f"Observed deviation {index}",
        "quality_attribute": "functional-suitability",
        "severity": "medium",
        "confidence": "high" if status == "confirmed" else "medium",
        "status": status,
        "summary": "An observation differed from the documented rule.",
        "expected": "The documented result.",
        "actual": "A different result.",
        "oracle": "The documented rule.",
        "reproduction": {
            "preconditions": ["Default configuration"],
            "steps": ["Run the recorded action", "Compare with the documented rule"],
            "reproducibility": reproducibility,
        },
        "attempt_ids": [attempt_id],
        "evidence": [{"kind": "test-output", "location": evidence}],
        "limitations": ["Synthetic seed record"],
        "acceptance_criteria": ["The documented result holds"],
        "suspected_root_cause": "unknown",
    }


def seed_ledger(target: Path, specs: Sequence[Mapping[str, Any]], revision: str) -> None:
    store = KitStore(target)
    store.initialize()
    for spec in specs:
        sid = spec["id"]
        store.create_session(
            {
                "id": sid,
                "objective": f"QA session {sid}",
                "mode": spec["mode"],
                "created_at": spec["created_at"],
                "target": {"root": ".", "revision": revision, "dirty": False, "runtime": ["Python 3.11"]},
                "scope": {"include": ["src/invoicing"], "exclude": []},
                "context": {
                    "intended_use": "Customer invoices",
                    "risk_tier": spec["risk_tier"],
                    "quality_attributes": spec["quality_attributes"],
                    "constraints": [],
                    "authorization_notes": ["Existing local tests are authorized"],
                },
                "charters": [_charter(spec["quality_attributes"])],
            }
        )
        for index, outcome in enumerate(spec["outcomes"], start=1):
            store.add_attempt(
                sid,
                {
                    "id": f"attempt-{index}",
                    "charter_id": "charter-main",
                    "started_at": spec["created_at"],
                    "duration_seconds": 5,
                    "action": "PYTHONPATH=src python -m unittest discover -s tests",
                    "environment": {"python": "3.11"},
                    "outcome": outcome,
                    "exit_code": 0 if outcome == "pass" else 1,
                    "observation": f"Recorded outcome: {outcome}",
                    "oracle": "The documented rule",
                    "evidence": [],
                },
            )
        evidence = f".agentic-qa/sessions/{sid}/evidence/run.txt"
        if spec["findings"]:
            (target / evidence).parent.mkdir(parents=True, exist_ok=True)
            (target / evidence).write_text(f"{sid}: recorded test output\n", encoding="utf-8")
        for index, status in enumerate(spec["findings"], start=1):
            store.add_finding(sid, _finding(index, status, "attempt-1", spec["created_at"], evidence))
        store.close_session(
            sid,
            "completed",
            {
                "disposition": "hold" if spec["findings"] else "acceptable",
                "summary": f"Seeded session {sid}",
                "limitations": ["Synthetic seed record"],
                "residual_risks": [],
                "next_actions": [],
            },
        )


def _seeding_stage(specs: Sequence[Mapping[str, Any]]):
    original = q02_claude_code.stage_fixture

    def stage(fixture: Mapping[str, Any], target: Path) -> str:
        head = original(fixture, target)
        seed_ledger(target, specs, head)
        q02_claude_code._git(target, "add", "--all")
        q02_claude_code._git(target, "commit", "--quiet", "--no-verify", "-m", "QA ledger")
        return q02_claude_code._git(target, "rev-parse", "HEAD")

    return stage


def report_facts(fixture: Mapping[str, Any], stdout: str, changed: Sequence[str], answer: str) -> dict[str, Any]:
    commands = parse_stream(stdout.splitlines())["commands"]
    return {
        "metrics_run": any("qa.py metrics" in c or "aqk metrics" in c for c in commands),
        "ledger_paths_changed": sorted(p for p in changed if p.startswith(".agentic-qa/")),
        "people_named": [name for name in fixture.get("people", []) if name.split()[0] in answer],
        "withheld_mentioned": any(word in answer.lower() for word in ("withheld", "too few", "too small", "small sample")),
    }


def run_command(args: argparse.Namespace) -> None:
    env = child_environment(args.config_dir)
    kit = install_location(_plugin_list(env), KIT)
    if Path(kit.get("read_from", "")).resolve() != PLUGIN_ROOT:
        raise LaneError("the lane must resolve the plugin in place to this working tree")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PLUGIN_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    suite = load_suite(SUITE)
    q02_claude_code.stage_fixture = _seeding_stage(suite["seed_sessions"])
    prompt = suite["prompt"] + SUFFIX
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for repeat in range(1, args.repeats + 1):
        fixture = {**suite["fixture"], "id": f"{suite['fixture']['id']}-{repeat}"}
        record = run_fixture(fixture, prompt, args.output, env, runner=_run, timeout=args.timeout)
        stdout = (args.output / "raw" / f"{fixture['id']}.jsonl").read_text(encoding="utf-8")
        record.update(report=report_facts(suite["fixture"], stdout, record["mechanical"]["changed_paths"], record["answer"]))
        records.append(record)
    result = {
        "suite_id": "Q15-G01",
        "lane": "claude-code",
        "surface": "cli",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claude_code_version": subprocess.run(
            ["claude", "--version"], env=dict(env), capture_output=True, text=True, check=False
        ).stdout.strip(),
        "plugin_revision": revision,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "limitations": [
            "Working-tree provenance: the skills as written at plugin_revision, not a published artifact.",
            "Headless `claude -p` CLI only, one Linux host.",
            "One seeded ledger of eight synthetic sessions; whether an answer ranked people is a reviewer's call.",
        ],
        "observations": records,
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output / "result.json"),
                "cases": {
                    r["case_id"]: {"status": r["mechanical"].get("status"), "failures": r["mechanical"].get("failures"), **r["report"]}
                    for r in records
                },
                "cost_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
            },
            indent=2,
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Q15 cross-session metrics evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--repeats", type=int, default=2, help="Fresh sessions")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per session")
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
