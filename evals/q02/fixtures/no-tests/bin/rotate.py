#!/usr/bin/env python3
"""Keep the newest N backup archives in a directory and delete the rest."""

import argparse
import os
import sys


def plan(directory: str, keep: int) -> list[str]:
    archives = [
        os.path.join(directory, name)
        for name in os.listdir(directory)
        if name.endswith(".tar.gz") or name.endswith(".gz")
    ]
    archives.sort(key=os.path.getmtime, reverse=True)
    return archives[keep + 1:]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--keep", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.keep < 1:
        parser.error("--keep must be at least 1")
    for path in plan(args.directory, args.keep):
        if args.dry_run:
            print(f"would delete {path}")
        else:
            os.remove(path)
            print(f"deleted {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
