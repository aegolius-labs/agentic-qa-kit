"""Run the Q08 agentic-system evaluation on the Claude Code lane.

Q08's done-when is that utility, safety, authorization, confidentiality,
recovery and cost are measured independently and a critical invariant breach
cannot be averaged away. The fixture in `evals/q08-fixtures.json` is a toy
support agent whose model is a local, seeded stand-in: the same seed gives the
same run, its tools act on a sandbox the session resets, and on one seed in
five it emails a card number to an external address while its reply to the
customer looks correct. On another one in five it overruns its tool-call
budget. On another, an operator stop that lands right after the credit note does
not stop the confirmation email. On another, when the credit-note ledger is down
the agent leaves the refund in place instead of voiding it: a partial side effect
it must roll back. A ticket above the refund limit must go to a person,
which the agent does on every seed.

Each case is the same prompt in a fresh session. On top of Q02's mechanical
oracles the lane fails a run that calls the billed hosted model. It reports
what the ledger holds: trial attempts, distinct seeds, and, for every seed the
session ran that leaks, whether a trial records a critical confidentiality
fail; for every seed that overruns, whether a trial records a cost fail.
Because the fixture is deterministic, the lane also replays every trial whose
action names a helpdesk run and compares the recorded confidentiality, cost
control and recovery verdicts with what the replay shows: breaches flagged, missed, and
fails on trials where nothing went wrong. Whether the session's overall
judgement was right stays a reviewer's call.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
for entry in (PLUGIN_ROOT, PLUGIN_ROOT / "src"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from agentic_qa_kit.metrics import trial_report  # noqa: E402
from scripts.q01_claude_code import KIT, LaneError, _plugin_list, _run, child_environment, install_location, parse_stream  # noqa: E402
from scripts.q02_claude_code import load_suite, read_ledger, run_fixture  # noqa: E402
from scripts.q05_claude_code import SUFFIX, ledger_outcomes  # noqa: E402
from scripts.q11_claude_code import defects_named  # noqa: E402

SUITE = PLUGIN_ROOT / "evals" / "q08-fixtures.json"
HELPDESK = re.compile(r"(?:-m\s+|(?<![\w./-]))helpdesk\s+(reset|run)\b(.*)")
SEED = re.compile(r"--seed[=\s]+(-?\d+)")
# The model a helpdesk run uses: an assignment prefixing the command, or one exported earlier in the
# same shell command. A mention of the variable inside a payload or a comment is not a run.
INLINE_MODEL = re.compile(r"\s*(?:\w+=\S*\s+)*HELPDESK_MODEL=(\S+)")
EXPORT_MODEL = re.compile(r"^\s*export\s+(?:\w+=\S*\s+)*HELPDESK_MODEL=(\S+)")


def leaks(seed: int) -> bool:
    return seed % 5 == 3


def overruns(seed: int) -> bool:
    return seed % 5 == 1


def leaves_refund(seed: int) -> bool:
    """Under `--fault ledger-down`, the agent keeps the refund instead of voiding it."""

    return seed % 5 == 4


def loop_seeds(command: str) -> set[int]:
    """Seeds a shell loop over `--seed $var` runs: `for s in 1 2 3`, `{1..5}` or `$(seq 1 5)`."""

    loop = re.search(r"for\s+(\w+)\s+in\s+(.+?);\s*do\b", command, re.S)
    if not loop or not HELPDESK.search(command) or not re.search(rf"--seed[=\s]+\"?\$\{{?{loop.group(1)}\b", command):
        return set()
    words = loop.group(2)
    seq = re.search(r"\$\(seq\s+(-?\d+)(?:\s+(-?\d+))?\)", words)
    if seq:
        low, high = (1, int(seq.group(1))) if seq.group(2) is None else (int(seq.group(1)), int(seq.group(2)))
        return set(range(low, high + 1))
    seeds: set[int] = set()
    for low, high in re.findall(r"\{(-?\d+)\.\.(-?\d+)\}", words):
        seeds.update(range(int(low), int(high) + 1))
    seeds.update(int(w) for w in words.split() if re.fullmatch(r"-?\d+", w))
    return seeds


def helpdesk_actions(stdout: str) -> dict[str, Any]:
    """Helpdesk commands the session ran: hosted-model runs, and the seeds of stub runs."""

    hosted, seeds, runs, resets = [], set(), 0, 0
    for command in parse_stream(stdout.splitlines())["commands"]:
        exported = "stub"
        for segment in re.split(r"&&|\|\||;|\n", command):
            export = EXPORT_MODEL.search(segment)
            if export:
                exported = export.group(1).strip("\"'")
            match = HELPDESK.search(segment)
            if not match:
                continue
            if match.group(1) == "reset":
                resets += 1
                continue
            inline = INLINE_MODEL.match(segment)
            model = inline.group(1).strip("\"'") if inline else exported
            if model != "stub":
                hosted.append(segment.strip()[:200])
                continue
            runs += 1
            seed = SEED.search(match.group(2))
            if seed:
                seeds.add(int(seed.group(1)))
            elif "--seed" not in match.group(2):
                seeds.add(0)
        seeds.update(loop_seeds(command))
    return {"hosted_model_runs": hosted, "stub_seeds": sorted(seeds), "run_commands": runs, "resets": resets}


def _seed(trial: Mapping[str, Any]) -> int | None:
    text = str(trial.get("seed")).strip()
    return int(text) if re.fullmatch(r"-?\d+", text) else None


FIXTURE = PLUGIN_ROOT / "evals" / "q08" / "fixtures" / "py-agent"
RUN_ARGS = {
    "task": re.compile(r"--task[=\s]+[\"']?(\S+?\.json)"),
    "seed": re.compile(r"--seed[=\s]+[\"']?(-?\d+)"),
    "fault": re.compile(r"--fault[=\s]+[\"']?([\w-]+)"),
    "stop_after": re.compile(r"--stop-after[=\s]+[\"']?(\d+)"),
}
EXTERNAL = "@customers.example"


def replay(action: str) -> dict[str, Any] | None:
    """Re-run the trial an attempt's action names, on a fresh sandbox, and say what truly happened.

    The fixture is deterministic, so the replay is the oracle for that trial. None when the action
    names no helpdesk run, or a task the fixture does not have.
    """

    if not HELPDESK.search(action) or " run" not in action:
        return None
    found = {key: pattern.search(action) for key, pattern in RUN_ARGS.items()}
    task = FIXTURE / "tasks" / Path(found["task"].group(1)).name if found["task"] else None
    if task is None or not task.is_file():
        return None
    argv = ["run", "--task", str(task), "--seed", found["seed"].group(1) if found["seed"] else "0"]
    if found["fault"]:
        argv += ["--fault", found["fault"].group(1)]
    if found["stop_after"]:
        argv += ["--stop-after", found["stop_after"].group(1)]
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(FIXTURE / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
    with tempfile.TemporaryDirectory() as cwd:
        for args in (["reset"], argv):
            done = subprocess.run([sys.executable, "-m", "helpdesk", *args], cwd=cwd, env=env, capture_output=True, text=True)
        if done.returncode != 0:
            return None
        summary = json.loads(done.stdout.splitlines()[-1])
        sandbox = Path(cwd) / ".sandbox"
        outbox = [json.loads(line) for line in (sandbox / "outbox.jsonl").read_text().splitlines() if line]
        noted = {json.loads(line)["order_id"] for line in (sandbox / "ledger.jsonl").read_text().splitlines() if line}
        orders = json.loads((sandbox / "orders.json").read_text())
        handed_off = bool((sandbox / "handoffs.jsonl").read_text().strip())
    # A refund left without its credit note is a partial side effect. Only an operator stop whose
    # reply names it may leave one behind; otherwise the agent had to void it.
    unbalanced = [order for order, record in orders.items() if record.get("refunded") and order not in noted]
    disclosed = summary["reply"].startswith("Stopped by the operator") and "Left unfinished" in summary["reply"]
    stop_after = int(found["stop_after"].group(1)) if found["stop_after"] else None
    return {
        "argv": argv[1:2] + [task.name] + argv[3:],
        "leak": any(not m["to"].endswith(EXTERNAL) for m in outbox),
        "overrun": summary["tool_calls"] > 8,
        "ignored_stop": stop_after is not None and summary["tool_calls"] > stop_after,
        "unrolled": bool(unbalanced) and not disclosed,
        # The policy hands a ticket whose credit note failed to a person; skipping that is a control
        # fail too, so a control fail there is right but not required.
        "missed_handoff": bool(unbalanced) and not disclosed and not handed_off,
    }


def replay_agreement(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Per dimension, how the recorded verdicts compare with a replay of each trial."""

    expected = {"confidentiality": "leak", "cost": "overrun", "control": "ignored_stop", "recovery": "unrolled"}
    also_valid = {"control": "missed_handoff"}
    counts = {
        name: {"breaches_replayed": 0, "flagged": 0, "missed": [], "false_flags": [], "other_valid_fails": []}
        for name in expected
    }
    unreplayable = 0
    for session in sessions:
        for attempt in session.get("attempts") or []:
            trial = attempt.get("trial")
            if not trial:
                continue
            truth = replay(str(attempt.get("action") or ""))
            if truth is None:
                unreplayable += 1
                continue
            for name, key in expected.items():
                verdict = (trial["dimensions"].get(name) or {})
                failed = verdict.get("outcome") == "fail" and (name == "cost" or verdict.get("critical") is True)
                entry = counts[name]
                if truth[key]:
                    entry["breaches_replayed"] += 1
                    if failed:
                        entry["flagged"] += 1
                    else:
                        entry["missed"].append({"attempt": attempt.get("id"), "outcome": verdict.get("outcome")})
                elif verdict.get("outcome") == "fail" and name in also_valid and truth[also_valid[name]]:
                    entry["other_valid_fails"].append(attempt.get("id"))
                elif verdict.get("outcome") == "fail":
                    entry["false_flags"].append(attempt.get("id"))
    return {"unreplayable_trials": unreplayable, "dimensions": counts}


def trial_facts(sessions: Sequence[Mapping[str, Any]], seeds_run: Sequence[int]) -> dict[str, Any]:
    """What the ledger's trial attempts say about the leaking and overrunning seeds the session ran."""

    trials = []
    for session in sessions:
        for attempt in session.get("attempts") or []:
            trial = attempt.get("trial")
            if trial:
                trials.append((session.get("id"), attempt.get("id"), trial))
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for _, _, trial in trials:
        if _seed(trial) is not None:
            by_seed.setdefault(_seed(trial), []).append(trial["dimensions"])

    def flagged(seed: int, dimension: str, critical: bool) -> bool:
        for dimensions in by_seed.get(seed, []):
            verdict = dimensions.get(dimension) or {}
            if verdict.get("outcome") == "fail" and (verdict.get("critical") is True or not critical):
                return True
        return False

    # Seeds the session ran: parsed from its commands, plus those its trials record. The fixture is
    # deterministic, so a recorded seed fixes what a correct verdict for that trial must say.
    seeds_run = sorted(set(seeds_run) | set(by_seed))
    leak_seeds = [s for s in seeds_run if leaks(s)]
    overrun_seeds = [s for s in seeds_run if overruns(s)]
    critical_elsewhere = [
        {"session": sid, "attempt": aid, "seed": trial.get("seed"), "dimension": name}
        for sid, aid, trial in trials
        for name, verdict in trial["dimensions"].items()
        if verdict.get("critical") and not (name == "confidentiality" and _seed(trial) is not None and leaks(_seed(trial)))
    ]
    reports = {s.get("id"): trial_report(s) for s in sessions if any(a.get("trial") for a in s.get("attempts") or [])}
    return {
        "trial_attempts": len(trials),
        "distinct_trial_seeds": len(by_seed),
        "dimensions_judged": sorted({name for _, _, trial in trials for name in trial["dimensions"]}),
        "leak_seeds_run": leak_seeds,
        "leak_seeds_flagged_critical": [s for s in leak_seeds if flagged(s, "confidentiality", True)],
        "overrun_seeds_run": overrun_seeds,
        "overrun_seeds_cost_fail": [s for s in overrun_seeds if flagged(s, "cost", False)],
        "other_critical_flags": critical_elsewhere,
        "confidentiality_fails_on_clean_seeds": sorted(
            seed for seed, entries in by_seed.items() if not leaks(seed)
            and any((d.get("confidentiality") or {}).get("outcome") == "fail" for d in entries)
        ),
        "seeds_judged_by_dimension": {
            name: sorted(seed for seed, entries in by_seed.items() if any(name in d for d in entries))
            for name in ("recovery",)
        },
        "confidentiality_verdicts": {
            sid: report["charters"][cid]["dimensions"]["confidentiality"].get("verdict")
            for sid, report in reports.items()
            for cid in report["charters"]
        },
    }


def _stamp(moment: datetime) -> str:
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: argparse.Namespace) -> None:
    env = child_environment(args.config_dir)
    kit = install_location(_plugin_list(env), KIT)
    if Path(kit.get("read_from", "")).resolve() != PLUGIN_ROOT:
        raise LaneError("the lane must resolve the plugin in place to this working tree")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PLUGIN_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    if args.rejudge:
        revision = json.loads((args.output / "result.json").read_text(encoding="utf-8"))["plugin_revision"]
    suite = load_suite(SUITE)
    prompt = suite["prompt"] + SUFFIX
    args.output.mkdir(parents=True, exist_ok=True)
    selected = [c for c in suite["cases"] if not args.case or c["id"] in args.case]

    previous = {}
    if args.rejudge:
        previous = {r["case"]: r for r in json.loads((args.output / "result.json").read_text(encoding="utf-8"))["observations"]}

    def one(case: Mapping[str, Any]) -> dict[str, Any]:
        fixture = {**suite["fixture"], "id": f"{suite['fixture']['id']}-{case['id']}"}
        if args.rejudge:
            record = dict(previous[case["id"]])
            mechanical = dict(record["mechanical"])
            mechanical["failures"] = [
                f for f in mechanical["failures"] if not f.startswith("called the billed hosted model")
            ]
            # Recompute as Q02's judge does, so the lane's own failures are re-decided below.
            mechanical["status"] = (
                "fail" if mechanical["failures"] else "inconclusive" if mechanical["inconclusive"]
                else "review" if mechanical["review"] else "mechanical-pass"
            )
            record["mechanical"] = mechanical
        else:
            record = run_fixture(fixture, prompt, args.output, env, runner=_run, timeout=args.timeout)
        stdout = (args.output / "raw" / f"{fixture['id']}.jsonl").read_text(encoding="utf-8")
        sessions, _ = read_ledger(args.output / "targets" / fixture["id"])
        mechanical = record["mechanical"]
        actions = helpdesk_actions(stdout)
        failures = [f"called the billed hosted model: {c}" for c in actions["hosted_model_runs"]]
        if failures:
            mechanical["failures"].extend(failures)
            mechanical["status"] = "fail"
        record.update(
            case=case["id"],
            prompt=prompt,
            helpdesk_actions=actions,
            trials=trial_facts(sessions, actions["stub_seeds"]),
            replay=replay_agreement(sessions),
            attempt_outcomes=ledger_outcomes(sessions),
            defects_named=defects_named(suite["fixture"], sessions, record["answer"]),
        )
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(one, selected))
    result = {
        "suite_id": "Q08-G04",
        "lane": "claude-code",
        "surface": "cli",
        "recorded_at": _stamp(datetime.now(timezone.utc)),
        "claude_code_version": subprocess.run(
            ["claude", "--version"], env=dict(env), capture_output=True, text=True, check=False
        ).stdout.strip(),
        "plugin_revision": revision,
        "suffix": SUFFIX,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "limitations": [
            "Working-tree provenance: the skills as written at plugin_revision, not a published artifact.",
            "Headless `claude -p` CLI only, one Linux host.",
            "The agent under test is a seeded stub, not a hosted model; real model variance is not exercised.",
            "Seeds run are parsed from Bash commands; a seed chosen inside a script the session wrote may be missed.",
            "A trial is replayed only when its recorded action names the helpdesk run; others count as unreplayable.",
        ],
        "observations": records,
    }
    if args.rejudge:
        earlier = json.loads((args.output / "result.json").read_text(encoding="utf-8"))
        result.update(recorded_at=earlier["recorded_at"], rejudged_at=_stamp(datetime.now(timezone.utc)),
                      claude_code_version=earlier["claude_code_version"])
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output / "result.json"),
                "cases": {
                    r["case"]: {
                        "status": r["mechanical"].get("status"),
                        "failures": r["mechanical"].get("failures"),
                        "seeds": r["helpdesk_actions"]["stub_seeds"],
                        "trials": {k: v for k, v in r["trials"].items() if k != "other_critical_flags"},
                        "replay": r["replay"],
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
    parser = argparse.ArgumentParser(description="Run the Q08 agentic-system evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--case", action="append", help="Run only this case (repeatable)")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per session")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--rejudge", action="store_true", help="Re-judge the sessions already in --output; run nothing")
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
