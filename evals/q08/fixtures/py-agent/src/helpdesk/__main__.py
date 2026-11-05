"""helpdesk reset | stop | run --task PATH --seed N [--fault email-timeout|ledger-down] [--stop-after N]"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .agent import ToolError, reset, run, stop

HOSTED_URL = "https://api.model-provider.example"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="helpdesk")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("reset")
    sub.add_parser("stop")
    runner = sub.add_parser("run")
    runner.add_argument("--task", required=True)
    runner.add_argument("--seed", type=int, default=0)
    runner.add_argument("--fault", choices=["email-timeout", "ledger-down"])
    runner.add_argument("--stop-after", type=int, help="Send the operator's stop after this many tool calls")
    args = parser.parse_args(argv)
    if args.command == "reset":
        reset()
        print("sandbox reset")
        return 0
    if args.command == "stop":
        try:
            stop()
        except ToolError as error:
            print(f"helpdesk: {error}", file=sys.stderr)
            return 1
        print("stop sent")
        return 0
    model = os.environ.get("HELPDESK_MODEL", "stub")
    if model != "stub":
        if not os.environ.get("HELPDESK_API_KEY"):
            print(f"helpdesk: the hosted model at {HOSTED_URL} needs HELPDESK_API_KEY", file=sys.stderr)
        else:
            print(f"helpdesk: refusing to call {HOSTED_URL} from this checkout", file=sys.stderr)
        return 2
    task = json.loads(Path(args.task).read_text(encoding="utf-8"))
    try:
        summary = run(task, args.seed, args.fault, args.stop_after)
    except ToolError as error:
        print(f"helpdesk: {error}", file=sys.stderr)
        return 1
    print(summary["reply"])
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
