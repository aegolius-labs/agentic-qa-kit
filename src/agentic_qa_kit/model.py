from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
RISK_TIERS = {"low", "medium", "high", "critical"}
SESSION_MODES = {
    "full",
    "discovery",
    "functional",
    "exploratory",
    "regression",
    "static",
    "integration",
    "non-functional",
    "reproduction",
    "evidence",
}
SESSION_STATUSES = {"planned", "running", "completed", "blocked"}
TERMINAL_SESSION_STATUSES = {"completed", "blocked"}
# Version 2 adds the receipt chain (Q03). Version 1 sessions stay readable,
# unchained, until `migrate` seals them.
SESSION_SCHEMA_VERSION = 2
SESSION_SCHEMA_VERSIONS = {1, 2}
CHARTER_STATUSES = {"planned", "running", "completed", "blocked"}
ATTEMPT_OUTCOMES = {"pass", "fail", "inconclusive", "error"}
# Test-design techniques an obligation can come from (Q04).
DESIGN_TECHNIQUES = {
    "partition",
    "boundary",
    "decision-table",
    "state-transition",
    "scenario",
    "combinatorial",
    "property",
    "other",
}
FINDING_STATUSES = {"candidate", "confirmed", "not-reproduced", "dismissed"}
FINDING_SEVERITIES = {"blocker", "critical", "high", "medium", "low"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
REPRODUCIBILITY = {"always", "intermittent", "once", "not-reproduced"}
QUALITY_ATTRIBUTES = {
    "functional-suitability",
    "performance-efficiency",
    "compatibility",
    "interaction-capability",
    "reliability",
    "security",
    "maintainability",
    "flexibility",
    "safety",
    "data-integrity",
    "observability",
    "other",
}


class ValidationError(ValueError):
    """Raised when a QA artifact violates its contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_id(prefix: str, payload: Any, length: int = 12) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()[:length]
    return f"{prefix}-{digest}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected a JSON object in {path}")
    return value


def _expect_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def _expect_list(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{path} must be an array")
    if nonempty and not value:
        raise ValidationError(f"{path} must not be empty")
    return value


def _expect_string(value: Any, path: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        qualifier = "a non-empty string" if nonempty else "a string"
        raise ValidationError(f"{path} must be {qualifier}")
    return value


def _expect_string_list(value: Any, path: str, *, nonempty: bool = False) -> list[str]:
    items = _expect_list(value, path, nonempty=nonempty)
    for index, item in enumerate(items):
        _expect_string(item, f"{path}[{index}]")
    return items


def _expect_id(value: Any, path: str) -> str:
    text = _expect_string(value, path)
    if not ID_RE.fullmatch(text):
        raise ValidationError(f"{path} must match {ID_RE.pattern}")
    return text


def _expect_enum(value: Any, allowed: set[str], path: str) -> str:
    text = _expect_string(value, path)
    if text not in allowed:
        raise ValidationError(f"{path} must be one of: {', '.join(sorted(allowed))}")
    return text


def _expect_int(value: Any, path: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{path} must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{path} must be at least {minimum}")
    return value


def _reject_unknown(payload: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValidationError(f"{path} contains unsupported fields: {', '.join(unknown)}")


def validate_manifest(payload: dict[str, Any]) -> None:
    _reject_unknown(
        payload,
        {"schema_version", "project", "defaults", "quality_profile", "authorization", "backlog"},
        "manifest",
    )
    if payload.get("schema_version") != 1:
        raise ValidationError("manifest.schema_version must be 1")

    project = _expect_object(payload.get("project"), "manifest.project")
    _reject_unknown(project, {"name", "repository_root"}, "manifest.project")
    _expect_string(project.get("name"), "manifest.project.name")
    _expect_string(project.get("repository_root"), "manifest.project.repository_root")

    defaults = _expect_object(payload.get("defaults"), "manifest.defaults")
    _reject_unknown(
        defaults,
        {"risk_tier", "evidence_root", "max_session_minutes", "max_reproduction_attempts"},
        "manifest.defaults",
    )
    _expect_enum(defaults.get("risk_tier"), RISK_TIERS, "manifest.defaults.risk_tier")
    evidence_root = _expect_string(defaults.get("evidence_root"), "manifest.defaults.evidence_root")
    if Path(evidence_root).is_absolute() or ".." in Path(evidence_root).parts:
        raise ValidationError("manifest.defaults.evidence_root must stay inside the target repository")
    _expect_int(defaults.get("max_session_minutes"), "manifest.defaults.max_session_minutes", 1)
    _expect_int(defaults.get("max_reproduction_attempts"), "manifest.defaults.max_reproduction_attempts", 1)

    profile = _expect_list(payload.get("quality_profile"), "manifest.quality_profile")
    for index, entry_value in enumerate(profile):
        entry = _expect_object(entry_value, f"manifest.quality_profile[{index}]")
        _reject_unknown(entry, {"attribute", "claim", "acceptance", "owner"}, f"manifest.quality_profile[{index}]")
        _expect_enum(entry.get("attribute"), QUALITY_ATTRIBUTES, f"manifest.quality_profile[{index}].attribute")
        _expect_string(entry.get("claim"), f"manifest.quality_profile[{index}].claim")
        _expect_string(entry.get("acceptance"), f"manifest.quality_profile[{index}].acceptance")
        owner = entry.get("owner")
        if owner is not None:
            _expect_string(owner, f"manifest.quality_profile[{index}].owner")

    authorization = _expect_object(payload.get("authorization"), "manifest.authorization")
    _reject_unknown(authorization, {"allowed", "requires_approval", "forbidden"}, "manifest.authorization")
    for field in ("allowed", "requires_approval", "forbidden"):
        _expect_string_list(authorization.get(field), f"manifest.authorization.{field}")
    categories = [item for field in authorization.values() for item in field]
    if len(categories) != len(set(categories)):
        raise ValidationError("manifest.authorization action classes must be mutually exclusive")

    backlog = _expect_object(payload.get("backlog"), "manifest.backlog")
    _reject_unknown(backlog, {"plugin", "mode"}, "manifest.backlog")
    _expect_string(backlog.get("plugin"), "manifest.backlog.plugin")
    _expect_enum(backlog.get("mode"), {"handoff-only", "disabled"}, "manifest.backlog.mode")


def validate_evidence(value: Any, path: str) -> list[dict[str, Any]]:
    evidence = _expect_list(value, path)
    for index, entry_value in enumerate(evidence):
        entry_path = f"{path}[{index}]"
        entry = _expect_object(entry_value, entry_path)
        _reject_unknown(entry, {"kind", "location", "digest", "description"}, entry_path)
        _expect_string(entry.get("kind"), f"{entry_path}.kind")
        _expect_string(entry.get("location"), f"{entry_path}.location")
        for optional in ("digest", "description"):
            if entry.get(optional) is not None:
                _expect_string(entry.get(optional), f"{entry_path}.{optional}")
    return evidence


def validate_charter(value: Any, path: str) -> None:
    charter = _expect_object(value, path)
    _reject_unknown(
        charter,
        {
            "id",
            "title",
            "objective",
            "risks",
            "quality_attributes",
            "methods",
            "oracle",
            "budget",
            "stop_conditions",
            "status",
            "obligations",
        },
        path,
    )
    _expect_id(charter.get("id"), f"{path}.id")
    _expect_string(charter.get("title"), f"{path}.title")
    _expect_string(charter.get("objective"), f"{path}.objective")
    _expect_string_list(charter.get("risks"), f"{path}.risks", nonempty=True)
    attributes = _expect_string_list(charter.get("quality_attributes"), f"{path}.quality_attributes", nonempty=True)
    for index, attribute in enumerate(attributes):
        _expect_enum(attribute, QUALITY_ATTRIBUTES, f"{path}.quality_attributes[{index}]")
    _expect_string_list(charter.get("methods"), f"{path}.methods", nonempty=True)
    _expect_string(charter.get("oracle"), f"{path}.oracle")
    budget = _expect_object(charter.get("budget"), f"{path}.budget")
    _reject_unknown(budget, {"minutes", "attempts"}, f"{path}.budget")
    _expect_int(budget.get("minutes"), f"{path}.budget.minutes", 1)
    _expect_int(budget.get("attempts"), f"{path}.budget.attempts", 1)
    _expect_string_list(charter.get("stop_conditions"), f"{path}.stop_conditions", nonempty=True)
    _expect_enum(charter.get("status"), CHARTER_STATUSES, f"{path}.status")
    if "obligations" in charter:
        validate_obligations(charter["obligations"], f"{path}.obligations")


def validate_obligations(value: Any, path: str) -> None:
    """A charter's test obligations: what the design says must be exercised."""

    obligations = _expect_list(value, path)
    seen: set[str] = set()
    for index, entry_value in enumerate(obligations):
        entry_path = f"{path}[{index}]"
        entry = _expect_object(entry_value, entry_path)
        _reject_unknown(entry, {"id", "technique", "source", "statement", "oracle"}, entry_path)
        obligation_id = _expect_id(entry.get("id"), f"{entry_path}.id")
        if obligation_id in seen:
            raise ValidationError(f"{path} IDs must be unique: {obligation_id}")
        seen.add(obligation_id)
        _expect_enum(entry.get("technique"), DESIGN_TECHNIQUES, f"{entry_path}.technique")
        for field in ("source", "statement", "oracle"):
            _expect_string(entry.get(field), f"{entry_path}.{field}")


def check_obligation_links(attempt: dict[str, Any], charters: list[dict[str, Any]]) -> None:
    """An attempt may name only obligations of its own charter."""

    linked = attempt.get("obligation_ids") or []
    if not linked:
        return
    charter = next(item for item in charters if item["id"] == attempt["charter_id"])
    known = {item["id"] for item in charter.get("obligations") or []}
    unknown = sorted(set(linked) - known)
    if unknown:
        raise ValidationError(
            f"attempt {attempt['id']} names obligations not in charter {charter['id']}: {', '.join(unknown)}"
        )


def obligation_coverage(session: dict[str, Any]) -> dict[str, int]:
    """How many declared obligations an attempt exercised.

    `exercised` means a pass or fail was observed against the obligation;
    `inconclusive` means it was only attempted with an inconclusive or error
    outcome. This measures the design model, not the absence of defects.
    """

    outcomes: dict[tuple[str, str], set[str]] = {}
    for attempt in session["attempts"]:
        for obligation_id in attempt.get("obligation_ids") or []:
            outcomes.setdefault((attempt["charter_id"], obligation_id), set()).add(attempt["outcome"])
    counts = {"total": 0, "exercised": 0, "inconclusive": 0, "unexercised": 0}
    for charter in session["charters"]:
        for obligation in charter.get("obligations") or []:
            counts["total"] += 1
            seen = outcomes.get((charter["id"], obligation["id"]), set())
            if seen & {"pass", "fail"}:
                counts["exercised"] += 1
            elif seen:
                counts["inconclusive"] += 1
            else:
                counts["unexercised"] += 1
    return counts


def validate_attempt(payload: dict[str, Any]) -> None:
    _reject_unknown(
        payload,
        {
            "id",
            "charter_id",
            "started_at",
            "duration_seconds",
            "action",
            "environment",
            "outcome",
            "exit_code",
            "observation",
            "oracle",
            "evidence",
            "obligation_ids",
        },
        "attempt",
    )
    _expect_id(payload.get("id"), "attempt.id")
    _expect_id(payload.get("charter_id"), "attempt.charter_id")
    _expect_string(payload.get("started_at"), "attempt.started_at")
    duration = payload.get("duration_seconds")
    if duration is not None:
        _expect_int(duration, "attempt.duration_seconds", 0)
    _expect_string(payload.get("action"), "attempt.action")
    environment = _expect_object(payload.get("environment"), "attempt.environment")
    for key, value in environment.items():
        _expect_string(key, "attempt.environment key")
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            raise ValidationError(f"attempt.environment.{key} must be a scalar or null")
    _expect_enum(payload.get("outcome"), ATTEMPT_OUTCOMES, "attempt.outcome")
    exit_code = payload.get("exit_code")
    if exit_code is not None:
        _expect_int(exit_code, "attempt.exit_code")
    _expect_string(payload.get("observation"), "attempt.observation")
    _expect_string(payload.get("oracle"), "attempt.oracle")
    validate_evidence(payload.get("evidence"), "attempt.evidence")
    if "obligation_ids" in payload:
        for index, value in enumerate(_expect_list(payload["obligation_ids"], "attempt.obligation_ids")):
            _expect_id(value, f"attempt.obligation_ids[{index}]")


def normalize_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(payload)
    result.setdefault("started_at", utc_now())
    result.setdefault("duration_seconds", None)
    result.setdefault("exit_code", None)
    result.setdefault("environment", {})
    result.setdefault("evidence", [])
    if not result.get("id"):
        identity = {key: result.get(key) for key in ("charter_id", "started_at", "action", "observation")}
        result["id"] = stable_id("attempt", identity)
    validate_attempt(result)
    return result


def validate_finding(payload: dict[str, Any]) -> None:
    _reject_unknown(
        payload,
        {
            "id",
            "recorded_at",
            "title",
            "quality_attribute",
            "severity",
            "confidence",
            "status",
            "summary",
            "expected",
            "actual",
            "oracle",
            "reproduction",
            "attempt_ids",
            "evidence",
            "limitations",
            "acceptance_criteria",
            "suspected_root_cause",
        },
        "finding",
    )
    _expect_id(payload.get("id"), "finding.id")
    _expect_string(payload.get("recorded_at"), "finding.recorded_at")
    _expect_string(payload.get("title"), "finding.title")
    _expect_enum(payload.get("quality_attribute"), QUALITY_ATTRIBUTES, "finding.quality_attribute")
    _expect_enum(payload.get("severity"), FINDING_SEVERITIES, "finding.severity")
    _expect_enum(payload.get("confidence"), CONFIDENCE_LEVELS, "finding.confidence")
    status = _expect_enum(payload.get("status"), FINDING_STATUSES, "finding.status")
    _expect_string(payload.get("summary"), "finding.summary")
    _expect_string(payload.get("expected"), "finding.expected")
    _expect_string(payload.get("actual"), "finding.actual")
    _expect_string(payload.get("oracle"), "finding.oracle")
    reproduction = _expect_object(payload.get("reproduction"), "finding.reproduction")
    _reject_unknown(reproduction, {"preconditions", "steps", "reproducibility", "attempts"}, "finding.reproduction")
    _expect_string_list(reproduction.get("preconditions"), "finding.reproduction.preconditions")
    steps = _expect_string_list(reproduction.get("steps"), "finding.reproduction.steps")
    reproducibility = _expect_enum(
        reproduction.get("reproducibility"), REPRODUCIBILITY, "finding.reproduction.reproducibility"
    )
    _expect_int(reproduction.get("attempts"), "finding.reproduction.attempts", 0)
    attempt_ids = _expect_string_list(payload.get("attempt_ids"), "finding.attempt_ids")
    for index, attempt_id in enumerate(attempt_ids):
        _expect_id(attempt_id, f"finding.attempt_ids[{index}]")
    if len(attempt_ids) != len(set(attempt_ids)):
        raise ValidationError("finding.attempt_ids must be unique")
    if reproduction.get("attempts") != len(attempt_ids):
        raise ValidationError("finding.reproduction.attempts must equal the number of linked attempt_ids")
    evidence = validate_evidence(payload.get("evidence"), "finding.evidence")
    _expect_string_list(payload.get("limitations"), "finding.limitations")
    criteria = _expect_string_list(payload.get("acceptance_criteria"), "finding.acceptance_criteria")
    _expect_string(payload.get("suspected_root_cause"), "finding.suspected_root_cause")

    if status == "confirmed":
        if not steps:
            raise ValidationError("a confirmed finding requires reproduction steps")
        if reproducibility == "not-reproduced":
            raise ValidationError("a confirmed finding cannot use reproducibility 'not-reproduced'")
        if not evidence:
            raise ValidationError("a confirmed finding requires evidence")
        if not criteria:
            raise ValidationError("a confirmed finding requires acceptance criteria")
    if status == "not-reproduced" and reproducibility != "not-reproduced":
        raise ValidationError("a not-reproduced finding must use reproducibility 'not-reproduced'")


def normalize_finding(payload: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(payload)
    result.setdefault("recorded_at", utc_now())
    result.setdefault("attempt_ids", [])
    result.setdefault("evidence", [])
    result.setdefault("limitations", [])
    result.setdefault("acceptance_criteria", [])
    result.setdefault("suspected_root_cause", "unknown")
    if not result.get("id"):
        identity = {key: result.get(key) for key in ("title", "expected", "actual", "recorded_at")}
        result["id"] = stable_id("finding", identity)
    validate_finding(result)
    return result


def validate_session(payload: dict[str, Any]) -> None:
    _reject_unknown(
        payload,
        {
            "schema_version",
            "id",
            "objective",
            "mode",
            "status",
            "created_at",
            "closed_at",
            "continuation_of",
            "target",
            "scope",
            "context",
            "charters",
            "attempts",
            "findings",
            "gaps",
            "decision",
            "receipts",
        },
        "session",
    )
    version = payload.get("schema_version")
    if version not in SESSION_SCHEMA_VERSIONS:
        raise ValidationError("session.schema_version must be 1 or 2")
    if version == 1 and "receipts" in payload:
        raise ValidationError("a schema-version-1 session has no receipts; migrate it to version 2")
    if version == 2:
        from .receipts import validate_receipt_shape

        receipts = _expect_list(payload.get("receipts"), "session.receipts")
        for index, receipt in enumerate(receipts):
            validate_receipt_shape(receipt, f"session.receipts[{index}]")
    _expect_id(payload.get("id"), "session.id")
    _expect_string(payload.get("objective"), "session.objective")
    _expect_enum(payload.get("mode"), SESSION_MODES, "session.mode")
    status = _expect_enum(payload.get("status"), SESSION_STATUSES, "session.status")
    _expect_string(payload.get("created_at"), "session.created_at")
    closed_at = payload.get("closed_at")
    if closed_at is not None:
        _expect_string(closed_at, "session.closed_at")

    continuation = payload.get("continuation_of")
    if continuation is not None:
        continuation_obj = _expect_object(continuation, "session.continuation_of")
        _reject_unknown(continuation_obj, {"session_id", "finding_id"}, "session.continuation_of")
        _expect_id(continuation_obj.get("session_id"), "session.continuation_of.session_id")
        finding_id = continuation_obj.get("finding_id")
        if finding_id is not None:
            _expect_id(finding_id, "session.continuation_of.finding_id")

    target = _expect_object(payload.get("target"), "session.target")
    _reject_unknown(target, {"root", "revision", "dirty", "runtime"}, "session.target")
    _expect_string(target.get("root"), "session.target.root")
    _expect_string(target.get("revision"), "session.target.revision")
    if not isinstance(target.get("dirty"), bool):
        raise ValidationError("session.target.dirty must be a boolean")
    _expect_string_list(target.get("runtime"), "session.target.runtime")

    scope = _expect_object(payload.get("scope"), "session.scope")
    _reject_unknown(scope, {"include", "exclude"}, "session.scope")
    _expect_string_list(scope.get("include"), "session.scope.include", nonempty=True)
    _expect_string_list(scope.get("exclude"), "session.scope.exclude")

    context = _expect_object(payload.get("context"), "session.context")
    _reject_unknown(
        context,
        {"intended_use", "risk_tier", "quality_attributes", "constraints", "authorization_notes"},
        "session.context",
    )
    _expect_string(context.get("intended_use"), "session.context.intended_use")
    _expect_enum(context.get("risk_tier"), RISK_TIERS, "session.context.risk_tier")
    attributes = _expect_string_list(
        context.get("quality_attributes"), "session.context.quality_attributes", nonempty=True
    )
    for index, attribute in enumerate(attributes):
        _expect_enum(attribute, QUALITY_ATTRIBUTES, f"session.context.quality_attributes[{index}]")
    _expect_string_list(context.get("constraints"), "session.context.constraints")
    _expect_string_list(context.get("authorization_notes"), "session.context.authorization_notes")

    charters = _expect_list(payload.get("charters"), "session.charters", nonempty=True)
    charter_ids: list[str] = []
    for index, charter in enumerate(charters):
        validate_charter(charter, f"session.charters[{index}]")
        charter_ids.append(charter["id"])
    if len(charter_ids) != len(set(charter_ids)):
        raise ValidationError("session charter IDs must be unique")

    attempts = _expect_list(payload.get("attempts"), "session.attempts")
    attempt_ids: list[str] = []
    for index, attempt in enumerate(attempts):
        validate_attempt(_expect_object(attempt, f"session.attempts[{index}]"))
        if attempt["charter_id"] not in charter_ids:
            raise ValidationError(f"attempt {attempt['id']} references unknown charter {attempt['charter_id']}")
        check_obligation_links(attempt, charters)
        attempt_ids.append(attempt["id"])
    if len(attempt_ids) != len(set(attempt_ids)):
        raise ValidationError("session attempt IDs must be unique")

    findings = _expect_list(payload.get("findings"), "session.findings")
    finding_ids: list[str] = []
    for index, finding in enumerate(findings):
        validate_finding(_expect_object(finding, f"session.findings[{index}]"))
        unknown_attempts = sorted(set(finding["attempt_ids"]) - set(attempt_ids))
        if unknown_attempts:
            raise ValidationError(
                f"finding {finding['id']} references unknown attempts: {', '.join(unknown_attempts)}"
            )
        finding_ids.append(finding["id"])
    if len(finding_ids) != len(set(finding_ids)):
        raise ValidationError("session finding IDs must be unique")
    if continuation is not None and continuation.get("finding_id") in finding_ids:
        raise ValidationError("a continuation cannot contain a replacement for its linked source finding")

    _expect_string_list(payload.get("gaps"), "session.gaps")
    decision = payload.get("decision")
    if status in TERMINAL_SESSION_STATUSES:
        if closed_at is None:
            raise ValidationError("a terminal session requires closed_at")
        decision_obj = _expect_object(decision, "session.decision")
        _reject_unknown(
            decision_obj,
            {"disposition", "summary", "limitations", "residual_risks", "next_actions"},
            "session.decision",
        )
        _expect_enum(
            decision_obj.get("disposition"), {"acceptable", "hold", "inconclusive"}, "session.decision.disposition"
        )
        _expect_string(decision_obj.get("summary"), "session.decision.summary")
        _expect_string_list(decision_obj.get("limitations"), "session.decision.limitations")
        _expect_string_list(decision_obj.get("residual_risks"), "session.decision.residual_risks")
        _expect_string_list(decision_obj.get("next_actions"), "session.decision.next_actions")
    elif closed_at is not None or decision is not None:
        raise ValidationError("a non-terminal session cannot contain closed_at or decision")


def normalize_session(payload: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(payload)
    result.setdefault("schema_version", SESSION_SCHEMA_VERSION)
    if result["schema_version"] == SESSION_SCHEMA_VERSION:
        result.setdefault("receipts", [])
    result.setdefault("created_at", utc_now())
    result.setdefault("status", "planned")
    result.setdefault("closed_at", None)
    result.setdefault("continuation_of", None)
    result.setdefault("attempts", [])
    result.setdefault("findings", [])
    result.setdefault("gaps", [])
    result.setdefault("decision", None)
    target = result.setdefault("target", {})
    if isinstance(target, dict):
        target.setdefault("runtime", [])
    if not result.get("id"):
        identity = {
            "objective": result.get("objective"),
            "mode": result.get("mode"),
            "created_at": result.get("created_at"),
            "target": result.get("target"),
        }
        result["id"] = stable_id("qa", identity)
    validate_session(result)
    return result


def validate_backlog_fields(payload: dict[str, Any]) -> None:
    _reject_unknown(
        payload,
        {
            "parent",
            "depends_on",
            "impact",
            "effort",
            "business_value",
            "enabler_value",
            "status",
            "maturity",
            "sprint",
        },
        "backlog fields",
    )
    parent = payload.get("parent")
    if parent is not None:
        _expect_id(parent, "backlog fields.parent")
    dependencies = _expect_string_list(payload.get("depends_on"), "backlog fields.depends_on")
    for index, dependency in enumerate(dependencies):
        _expect_id(dependency, f"backlog fields.depends_on[{index}]")
    for field in ("impact", "effort", "business_value"):
        value = _expect_int(payload.get(field), f"backlog fields.{field}", 1)
        if value > 5:
            raise ValidationError(f"backlog fields.{field} must be at most 5")
    enabler = _expect_int(payload.get("enabler_value"), "backlog fields.enabler_value", 0)
    if enabler > 5:
        raise ValidationError("backlog fields.enabler_value must be at most 5")
    _expect_string(payload.get("status"), "backlog fields.status")
    _expect_enum(payload.get("maturity"), {"refined", "ready"}, "backlog fields.maturity")
    sprint = payload.get("sprint")
    if sprint is not None:
        _expect_string(sprint, "backlog fields.sprint")
