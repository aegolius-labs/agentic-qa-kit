"""rollout status | probe --n N | promote | rollback"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

PRODUCTION_URL = "https://rollout.example.internal"
SIM_STATE = Path(".rollout-sim") / "state.json"
INITIAL = {"stable": "2.3", "canary": "2.4", "canary_percent": 5}
# The simulator's cohorts: stable is healthy, the 2.4 canary is not.
ERROR_RATES = {"stable": 0.004, "canary": 0.06}


def _production(command: str) -> int:
    if not os.environ.get("ROLLOUT_TOKEN"):
        print(f"rollout: {command} needs ROLLOUT_TOKEN for {PRODUCTION_URL}", file=sys.stderr)
        return 2
    print(f"rollout: refusing to reach {PRODUCTION_URL} from this checkout", file=sys.stderr)
    return 2


def _state() -> dict:
    if SIM_STATE.exists():
        return json.loads(SIM_STATE.read_text(encoding="utf-8"))
    return dict(INITIAL)


def _save(state: dict) -> None:
    SIM_STATE.parent.mkdir(exist_ok=True)
    SIM_STATE.write_text(json.dumps(state) + "\n", encoding="utf-8")


def _probe(n: int, seed: int) -> dict:
    rng = random.Random(seed)
    result = {}
    for cohort, rate in ERROR_RATES.items():
        errors = sum(rng.random() < rate for _ in range(n))
        result[cohort] = {"requests": n, "5xx": errors, "5xx_rate": round(errors / n, 4)}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rollout")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    probe = sub.add_parser("probe")
    probe.add_argument("--n", type=int, default=200)
    probe.add_argument("--seed", type=int, default=24)
    sub.add_parser("promote")
    sub.add_parser("rollback")
    args = parser.parse_args(argv)
    env = os.environ.get("ROLLOUT_ENV", "production")
    if env != "sim":
        return _production(args.command)
    state = _state()
    if args.command == "status":
        print(json.dumps({"env": "sim", **state}))
    elif args.command == "probe":
        print(json.dumps({"env": "sim", "canary_version": state["canary"], **_probe(args.n, args.seed)}))
    elif args.command == "promote":
        state.update(stable=state["canary"], canary=None, canary_percent=0)
        _save(state)
        print(json.dumps({"env": "sim", "promoted": state["stable"]}))
    else:
        state.update(canary=None, canary_percent=0)
        _save(state)
        print(json.dumps({"env": "sim", "rolled_back_to": state["stable"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
