from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .model import (
    FINDING_STATUSES,
    TERMINAL_SESSION_STATUSES,
    ValidationError,
    normalize_attempt,
    normalize_finding,
    normalize_session,
    read_json,
    utc_now,
    validate_manifest,
    validate_session,
)


FINDING_TRANSITIONS = {
    "candidate": FINDING_STATUSES,
    "confirmed": {"confirmed"},
    "not-reproduced": {"not-reproduced"},
    "dismissed": {"dismissed"},
}


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


class KitStore:
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.control_root = self.root / ".agentic-qa"
        self.manifest_path = self.control_root / "manifest.json"

    def default_manifest(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "project": {"name": self.root.name, "repository_root": "."},
            "defaults": {
                "risk_tier": "medium",
                "evidence_root": ".agentic-qa/sessions",
                "max_session_minutes": 60,
                "max_reproduction_attempts": 3,
            },
            "quality_profile": [],
            "authorization": {
                "allowed": ["read_repository", "run_existing_local_checks", "write_qa_evidence"],
                "requires_approval": [
                    "install_dependencies",
                    "change_source_or_tests",
                    "use_external_service",
                    "access_sensitive_data",
                    "run_load_or_fault_injection",
                    "touch_production",
                ],
                "forbidden": ["expose_secrets", "use_unapproved_production_data", "alter_oracles_to_force_pass"],
            },
            "backlog": {"plugin": "agentic-backlog-kit", "mode": "handoff-only"},
        }

    def initialize(self, *, force: bool = False) -> Path:
        if self.manifest_path.exists() and not force:
            raise ValidationError(f"manifest already exists: {self.manifest_path}")
        payload = self.default_manifest()
        validate_manifest(payload)
        atomic_write_json(self.manifest_path, payload)
        return self.manifest_path

    def load_manifest(self) -> dict[str, Any]:
        payload = read_json(self.manifest_path)
        validate_manifest(payload)
        return payload

    def _session_id(self, session_id: str) -> str:
        from .model import ID_RE

        if not ID_RE.fullmatch(session_id):
            raise ValidationError(f"invalid session ID: {session_id}")
        return session_id

    def session_path(self, session_id: str) -> Path:
        session_id = self._session_id(session_id)
        return self.control_root / "sessions" / session_id / "session.json"

    def create_session(self, input_payload: dict[str, Any]) -> dict[str, Any]:
        self.load_manifest()
        session = normalize_session(input_payload)
        path = self.session_path(session["id"])
        if path.exists():
            raise ValidationError(f"session already exists: {session['id']}")
        atomic_write_json(path, session)
        return session

    def load_session(self, session_id: str) -> dict[str, Any]:
        payload = read_json(self.session_path(session_id))
        validate_session(payload)
        return payload

    def save_session(self, payload: dict[str, Any]) -> None:
        validate_session(payload)
        atomic_write_json(self.session_path(payload["id"]), payload)

    def add_attempt(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("cannot add an attempt to a terminal session")
        attempt = normalize_attempt(input_payload)
        charter_ids = {charter["id"] for charter in session["charters"]}
        if attempt["charter_id"] not in charter_ids:
            raise ValidationError(f"unknown charter ID: {attempt['charter_id']}")
        if attempt["id"] in {item["id"] for item in session["attempts"]}:
            raise ValidationError(f"attempt already exists: {attempt['id']}")
        session["attempts"].append(attempt)
        if session["status"] == "planned":
            session["status"] = "running"
        for charter in session["charters"]:
            if charter["id"] == attempt["charter_id"] and charter["status"] == "planned":
                charter["status"] = "running"
        self.save_session(session)
        return attempt

    def add_finding(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("cannot add a finding to a terminal session")
        finding = normalize_finding(input_payload)
        if finding["id"] in {item["id"] for item in session["findings"]}:
            raise ValidationError(f"finding already exists: {finding['id']}")
        unknown_attempts = sorted(set(finding["attempt_ids"]) - {item["id"] for item in session["attempts"]})
        if unknown_attempts:
            raise ValidationError(f"finding references unknown attempts: {', '.join(unknown_attempts)}")
        session["findings"].append(finding)
        self.save_session(session)
        return finding

    def update_finding(self, session_id: str, finding_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("cannot update a finding in a terminal session")
        finding_index = next(
            (index for index, finding in enumerate(session["findings"]) if finding["id"] == finding_id), None
        )
        if finding_index is None:
            raise ValidationError(f"unknown finding ID: {finding_id}")
        current = session["findings"][finding_index]
        merged = dict(current)
        merged.update(input_payload)
        merged["id"] = finding_id
        updated = normalize_finding(merged)
        if updated["status"] not in FINDING_TRANSITIONS[current["status"]]:
            raise ValidationError(f"invalid finding transition: {current['status']} -> {updated['status']}")
        unknown_attempts = sorted(set(updated["attempt_ids"]) - {item["id"] for item in session["attempts"]})
        if unknown_attempts:
            raise ValidationError(f"finding references unknown attempts: {', '.join(unknown_attempts)}")
        session["findings"][finding_index] = updated
        self.save_session(session)
        return updated

    def close_session(self, session_id: str, status: str, decision: dict[str, Any]) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("session is already terminal")
        if status not in TERMINAL_SESSION_STATUSES:
            raise ValidationError("close status must be completed or blocked")
        session["status"] = status
        session["closed_at"] = utc_now()
        session["decision"] = decision
        for charter in session["charters"]:
            if charter["status"] in {"planned", "running"}:
                charter["status"] = "completed" if status == "completed" else "blocked"
        self.save_session(session)
        return session

    def list_sessions(self) -> list[dict[str, Any]]:
        sessions_root = self.control_root / "sessions"
        if not sessions_root.exists():
            return []
        sessions: list[dict[str, Any]] = []
        for path in sorted(sessions_root.glob("*/session.json")):
            payload = read_json(path)
            validate_session(payload)
            sessions.append(payload)
        return sessions

    def validate_all(self) -> dict[str, int]:
        self.load_manifest()
        sessions = self.list_sessions()
        return {
            "sessions": len(sessions),
            "attempts": sum(len(item["attempts"]) for item in sessions),
            "findings": sum(len(item["findings"]) for item in sessions),
        }
