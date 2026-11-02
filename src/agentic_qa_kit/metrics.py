"""Cross-session QA metrics with denominators, uncertainty and guardrails (Q15).

Every rate carries its numerator, its denominator and a 95% Wilson score
interval, and a rate whose denominator is below `MIN_DENOMINATOR` is withheld
rather than shown. Groups are properties of the work (quality attribute, mode,
risk tier), never of people: the ledger records no tester, and the one
person-shaped field it does hold, a production approver, is never read here.
Sessions whose receipt chain is broken are excluded and counted, not averaged
in. The output measures the QA process on this ledger. It is not a quality
score for the product, a target, or a ranking of anyone.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from .model import ATTEMPT_OUTCOMES, FINDING_STATUSES, ValidationError, obligation_coverage
from .receipts import integrity

GROUPINGS = ("quality-attribute", "mode", "risk-tier")
MIN_DENOMINATOR = 5
Z_95 = 1.959963984540054
GUARDRAILS = [
    "Groups are properties of the work, never of people; there is no per-person or per-agent view.",
    f"A rate with a denominator below {MIN_DENOMINATOR} is withheld, not shown.",
    "Each rate carries its numerator, denominator and a 95% Wilson interval; overlapping intervals are not a difference.",
    "Sessions with a broken receipt chain are excluded and counted, not averaged in.",
    "Counts of findings or attempts are not quality or productivity: do not set targets on them.",
    "These metrics describe this ledger's QA process, not the product's defect rate or release readiness.",
]


def wilson(successes: int, total: int) -> list[float] | None:
    if total <= 0:
        return None
    p = successes / total
    denominator = 1 + Z_95**2 / total
    centre = (p + Z_95**2 / (2 * total)) / denominator
    margin = Z_95 * math.sqrt(p * (1 - p) / total + Z_95**2 / (4 * total**2)) / denominator
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def rate(numerator: int, denominator: int) -> dict[str, Any]:
    result: dict[str, Any] = {"numerator": numerator, "denominator": denominator}
    if denominator < MIN_DENOMINATOR:
        result.update(value=None, interval_95=None, withheld=f"denominator below {MIN_DENOMINATOR}")
    else:
        result.update(value=round(numerator / denominator, 4), interval_95=wilson(numerator, denominator))
    return result


def _keys(session: dict[str, Any], by: str) -> list[str]:
    if by == "quality-attribute":
        return sorted(set(session["context"]["quality_attributes"]))
    if by == "mode":
        return [session["mode"]]
    return [session["context"]["risk_tier"]]


def _group(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = {outcome: 0 for outcome in sorted(ATTEMPT_OUTCOMES)}
    findings = {status: 0 for status in sorted(FINDING_STATUSES)}
    obligations = {"total": 0, "exercised": 0, "inconclusive": 0, "unexercised": 0}
    for session in sessions:
        for attempt in session["attempts"]:
            outcomes[attempt["outcome"]] += 1
        for finding in session["findings"]:
            findings[finding["status"]] += 1
        for key, value in obligation_coverage(session).items():
            obligations[key] += value
    attempts = sum(outcomes.values())
    resolved = findings["confirmed"] + findings["dismissed"] + findings["not-reproduced"]
    return {
        "sessions": len(sessions),
        "attempts": {"total": attempts, **outcomes},
        "findings": {"total": sum(findings.values()), **findings},
        "obligations": obligations,
        "rates": {
            # Attempts that could not reach a verdict: method or environment health.
            "inconclusive_or_error": rate(outcomes["inconclusive"] + outcomes["error"], attempts),
            # Of findings that reached a verdict, how many held up under reproduction.
            "confirmed_of_resolved_findings": rate(findings["confirmed"], resolved),
            # Of declared design obligations, how many saw a pass or fail.
            "obligations_exercised": rate(obligations["exercised"], obligations["total"]),
        },
    }


def compute(sessions: Iterable[dict[str, Any]], by: str = "quality-attribute") -> dict[str, Any]:
    if by not in GROUPINGS:
        raise ValidationError(f"metrics can group only by {', '.join(GROUPINGS)}; never by person")
    included: list[dict[str, Any]] = []
    excluded = {"broken_integrity": 0, "not_closed": 0}
    for session in sessions:
        if integrity(session) == "broken":
            excluded["broken_integrity"] += 1
        elif session["status"] not in {"completed", "blocked"}:
            excluded["not_closed"] += 1
        else:
            included.append(session)
    groups: dict[str, list[dict[str, Any]]] = {}
    for session in included:
        for key in _keys(session, by):
            groups.setdefault(key, []).append(session)
    created = sorted(session["created_at"] for session in included)
    return {
        "scope": {
            "sessions_included": len(included),
            "excluded": excluded,
            "window": {"first": created[0], "last": created[-1]} if created else None,
            "grouped_by": by,
            # A session with several quality attributes counts once in each.
            "groups_overlap": by == "quality-attribute",
        },
        "overall": _group(included),
        "groups": {key: _group(members) for key, members in sorted(groups.items())},
        "guardrails": GUARDRAILS,
    }
