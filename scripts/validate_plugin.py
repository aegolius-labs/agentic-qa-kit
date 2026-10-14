"""Run Claude Code's bundled plugin validator and fail on any unaccepted warning.

The two manifests are validated without --strict because each emits known,
accepted warnings (see CLAUDE.md). This script runs all three validations and
fails if a validation fails, if an accepted warning is missing from the
allowlist below, or if any other warning appears. skills/ must pass --strict.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# (target, strict, accepted warning prefixes)
CHECKS: tuple[tuple[str, bool, tuple[str, ...]], ...] = (
    (
        ".claude-plugin/plugin.json",
        False,
        (
            "version: No version specified",
            "root: CLAUDE.md at the plugin root is not loaded as project context",
        ),
    ),
    (
        ".claude-plugin/marketplace.json",
        False,
        ("plugins[0] plugin.json → version: No version specified",),
    ),
    ("skills", True, ()),
)


def warnings_in(output: str) -> list[str]:
    """Return the warning lines the validator prints as `  > message`."""

    return [
        line.strip()[1:].strip()
        for line in output.splitlines()
        if line.strip().startswith(">")
    ]


def unaccepted(warnings: list[str], accepted: tuple[str, ...]) -> list[str]:
    return [w for w in warnings if not any(w.startswith(a) for a in accepted)]


def main() -> int:
    claude = os.environ.get("CLAUDE_BIN", "claude")
    failed = False
    for target, strict, accepted in CHECKS:
        command = [claude, "plugin", "validate", target]
        if strict:
            command.append("--strict")
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout + result.stderr
        print(output)
        if result.returncode != 0:
            print(f"FAIL: {' '.join(command[1:])} exited {result.returncode}")
            failed = True
            continue
        extra = unaccepted(warnings_in(output), accepted)
        for warning in extra:
            print(f"FAIL: unaccepted warning from {target}: {warning}")
        failed = failed or bool(extra)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
