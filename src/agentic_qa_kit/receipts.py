"""Chained receipts for session mutations (Q03).

Every accepted change to a schema-version-2 session appends one receipt. A
receipt seals the canonical digest of the whole session as it stood after that
change, and links to the previous receipt's digest. Verification recomputes
the chain and compares its last state with the session on disk.

This detects an edit made outside the ledger, a removed or reordered receipt,
and a session whose later changes were dropped. It does not prove that any
recorded observation is true, and it does not stop someone who rewrites both
the session and every receipt after it: the chain carries no secret. It makes
tampering visible to anyone who did not also forge the chain.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .model import ValidationError


RECEIPT_OPERATIONS = {
    "session-create",
    "attempt-add",
    "finding-add",
    "finding-update",
    "session-close",
    "migrate",
}
RECEIPT_FIELDS = {"seq", "op", "subject", "at", "prev", "state", "digest"}


def canonical(payload: Any) -> bytes:
    """One byte form per JSON value: sorted keys, no insignificant whitespace."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(payload)).hexdigest()


def file_digest(path: Path) -> str:
    """SHA-256 of a file's bytes, in the same `sha256:<hex>` form."""

    hasher = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 16), b""):
            hasher.update(block)
    return "sha256:" + hasher.hexdigest()


def state_digest(session: dict[str, Any]) -> str:
    """Digest of everything in a session except its receipts."""

    return digest({key: value for key, value in session.items() if key != "receipts"})


def append_receipt(session: dict[str, Any], op: str, subject: str | None, at: str) -> dict[str, Any]:
    if op not in RECEIPT_OPERATIONS:
        raise ValidationError(f"unknown receipt operation: {op}")
    receipts = session.setdefault("receipts", [])
    receipt = {
        "seq": len(receipts) + 1,
        "op": op,
        "subject": subject,
        "at": at,
        "prev": receipts[-1]["digest"] if receipts else None,
        "state": state_digest(session),
    }
    receipt["digest"] = digest(receipt)
    receipts.append(receipt)
    return receipt


def validate_receipt_shape(receipt: Any, where: str) -> None:
    if not isinstance(receipt, dict):
        raise ValidationError(f"{where} must be an object")
    unknown = sorted(set(receipt) - RECEIPT_FIELDS)
    missing = sorted(RECEIPT_FIELDS - set(receipt))
    if unknown or missing:
        raise ValidationError(f"{where} has unknown fields {unknown} or is missing {missing}")
    if not isinstance(receipt["seq"], int) or isinstance(receipt["seq"], bool) or receipt["seq"] < 1:
        raise ValidationError(f"{where}.seq must be a positive integer")
    if receipt["op"] not in RECEIPT_OPERATIONS:
        raise ValidationError(f"{where}.op must be one of {sorted(RECEIPT_OPERATIONS)}")
    for field in ("state", "digest"):
        if not isinstance(receipt[field], str) or not receipt[field].startswith("sha256:"):
            raise ValidationError(f"{where}.{field} must be a sha256 digest")
    if receipt["prev"] is not None and not isinstance(receipt["prev"], str):
        raise ValidationError(f"{where}.prev must be a digest or null")
    if receipt["subject"] is not None and not isinstance(receipt["subject"], str):
        raise ValidationError(f"{where}.subject must be a string or null")
    if not isinstance(receipt["at"], str) or not receipt["at"]:
        raise ValidationError(f"{where}.at must be a non-empty string")


def chain_problems(session: dict[str, Any]) -> list[str]:
    """Every way the session disagrees with its receipt chain; empty when intact."""

    receipts = session.get("receipts") or []
    if not receipts:
        return ["the session has no receipts"]
    problems: list[str] = []
    previous = None
    for index, receipt in enumerate(receipts):
        if receipt["seq"] != index + 1:
            problems.append(f"receipt {index + 1} has seq {receipt['seq']}; a receipt is missing or out of order")
        if receipt["prev"] != previous:
            problems.append(f"receipt {receipt['seq']} does not link to the receipt before it")
        body = {key: value for key, value in receipt.items() if key != "digest"}
        if digest(body) != receipt["digest"]:
            problems.append(f"receipt {receipt['seq']} was altered after it was sealed")
        previous = receipt["digest"]
    if state_digest(session) != receipts[-1]["state"]:
        problems.append("the session differs from the state its last receipt sealed")
    return problems


def integrity(session: dict[str, Any]) -> str:
    """`chained`, `broken`, or `unchained` for a schema-version-1 session."""

    if session.get("schema_version") == 1:
        return "unchained"
    return "broken" if chain_problems(session) else "chained"
