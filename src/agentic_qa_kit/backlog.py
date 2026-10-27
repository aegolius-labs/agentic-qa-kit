from __future__ import annotations

from typing import Any

from .model import ValidationError, validate_backlog_fields


def _evidence_lines(finding: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for item in finding["evidence"]:
        description = f" — {item['description']}" if item.get("description") else ""
        digest = f" ({item['digest']})" if item.get("digest") else ""
        lines.append(f"- {item['kind']}: {item['location']}{digest}{description}")
    return lines


def backlog_source(session: dict[str, Any], finding: dict[str, Any]) -> str:
    return f"agentic-qa-kit:session={session['id']};finding={finding['id']}"


def build_backlog_item(session: dict[str, Any], finding: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    validate_backlog_fields(fields)
    if finding["status"] != "confirmed":
        raise ValidationError("only confirmed findings can be exported to the backlog")
    if not finding["evidence"]:
        raise ValidationError("a backlog export requires finding evidence")

    reproduction = finding["reproduction"]
    preconditions = "\n".join(f"- {value}" for value in reproduction["preconditions"]) or "- None recorded"
    steps = "\n".join(f"{index}. {value}" for index, value in enumerate(reproduction["steps"], start=1))
    evidence = "\n".join(_evidence_lines(finding))
    limitations = "\n".join(f"- {value}" for value in finding["limitations"]) or "- None recorded"
    description = (
        f"{finding['summary']}\n\n"
        f"QA session: `{session['id']}`\n"
        f"QA finding: `{finding['id']}`\n"
        f"Target revision: `{session['target']['revision']}` (dirty: {str(session['target']['dirty']).lower()})\n"
        f"Quality attribute: `{finding['quality_attribute']}`\n"
        f"QA severity: `{finding['severity']}`; confidence: `{finding['confidence']}`\n\n"
        f"Expected:\n{finding['expected']}\n\n"
        f"Actual:\n{finding['actual']}\n\n"
        f"Preconditions:\n{preconditions}\n\n"
        f"Reproduction ({reproduction['reproducibility']}, {reproduction['attempts']} attempts):\n{steps}\n\n"
        f"Oracle:\n{finding['oracle']}\n\n"
        f"Evidence:\n{evidence}\n\n"
        f"Limitations:\n{limitations}\n\n"
        f"Suspected root cause: {finding['suspected_root_cause']}"
    )
    return {
        "title": finding["title"],
        "type": "Bug",
        "description": description,
        "acceptance_criteria": list(finding["acceptance_criteria"]),
        "parent": fields["parent"],
        "depends_on": list(fields["depends_on"]),
        "impact": fields["impact"],
        "effort": fields["effort"],
        "business_value": fields["business_value"],
        "enabler_value": fields["enabler_value"],
        "status": fields["status"],
        "maturity": fields["maturity"],
        "sprint": fields["sprint"],
        # The receiving kit refuses a second item with the same source, so a
        # repeated handoff of this finding cannot become a second Bug.
        "source": backlog_source(session, finding),
    }
