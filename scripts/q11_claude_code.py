"""Run the Q11 suite-trust evaluation on the Claude Code lane.

Q11's done-when is that a session asked whether a suite can be trusted finds
the entropy a verdict depends on, separates product defects from test defects,
and changes no test, CI file or dependency to get there. The pack's text is
pinned by `tests/test_nfr_packs.py`; this lane checks the behavior on one
fixture (`evals/q11-fixtures.json`) whose CI retries a suite that fails on
about half of hash seeds and hides an order-dependent test.

On top of Q02's mechanical oracles, which already fail a run that installs a
dependency or edits a tracked file, it records whether the session read the
suite-trust pack, and which planted defects the findings and answer name. A
keyword hit is a discovery aid, not a classification verdict; whether each
cause was classified correctly stays a reviewer's call.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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

from scripts.q01_claude_code import KIT, LaneError, _plugin_list, _run, child_environment, install_location  # noqa: E402
from scripts.q02_claude_code import load_suite, read_ledger, run_fixture  # noqa: E402
from scripts.q05_claude_code import SUFFIX, ledger_outcomes, pack_reads  # noqa: E402

SUITE = PLUGIN_ROOT / "evals" / "q11-fixtures.json"
PACK = "suite-trust.md"
FINDING_TEXT = ("title", "summary", "expected", "actual", "suspected_root_cause")


def defects_named(fixture: Mapping[str, Any], sessions: Sequence[Mapping[str, Any]], answer: str) -> dict[str, list[str]]:
    """For each planted defect, the keywords that the findings or the final answer contain."""

    texts = [answer]
    for session in sessions:
        for finding in session.get("findings") or []:
            texts.extend(str(finding.get(field) or "") for field in FINDING_TEXT)
    haystack = "\n".join(texts).lower()
    return {
        defect["id"]: [word for word in defect["keywords"] if word.lower() in haystack]
        for defect in fixture.get("planted_defects", [])
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
    prompt = suite["prompt"] + SUFFIX
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [
        {**fixture, "id": f"{fixture['id']}-{repeat}", "fixture": fixture["id"]}
        for fixture in suite["fixtures"]
        for repeat in range(1, args.repeats + 1)
    ]

    def one(case: Mapping[str, Any]) -> dict[str, Any]:
        record = run_fixture(case, prompt, args.output, env, runner=_run, timeout=args.timeout)
        stdout = (args.output / "raw" / f"{case['id']}.jsonl").read_text(encoding="utf-8")
        sessions, _ = read_ledger(args.output / "targets" / case["id"])
        record.update(
            fixture=case["fixture"],
            pack=pack_reads(stdout, PACK),
            attempt_outcomes=ledger_outcomes(sessions),
            defects_named=defects_named(case, sessions, record["answer"]),
        )
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(one, cases))
    result = {
        "suite_id": "Q11-G01",
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
            "One small synthetic fixture with two planted causes; keyword hits are not classification verdicts.",
        ],
        "observations": records,
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output / "result.json"),
                "cases": {
                    r["case_id"]: {
                        "status": r["mechanical"].get("status"),
                        "pack_read": r["pack"]["expected_read"],
                        "outcomes": r["attempt_outcomes"],
                        "defects_named": {k: bool(v) for k, v in r["defects_named"].items()},
                    }
                    for r in records
                },
                "cost_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
            },
            indent=2,
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Q11 suite-trust evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--repeats", type=int, default=2, help="Fresh sessions per fixture")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per session")
    parser.add_argument("--workers", type=int, default=2)
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
