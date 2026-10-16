from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

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

# History a finding accumulates. Entries may be appended, never removed or
# rewritten, so an update cannot erase evidence that was already recorded.
APPEND_ONLY_FINDING_FIELDS = ("attempt_ids", "evidence", "limitations")
# What was observed. Fixed once a finding leaves `candidate`; a later
# observation belongs in a new attempt or a continuation, not in an edit.
SETTLED_FINDING_FIELDS = ("title", "summary", "expected", "actual", "oracle")


@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    """Hold an OS-level exclusive lock on `path` for one read-modify-write.

    The lock belongs to the open file, so the operating system releases it when
    the holder exits, even after a crash; there is no stale lock to clear.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    continue
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _check_finding_history(current: dict[str, Any], updated: dict[str, Any]) -> None:
    if updated["recorded_at"] != current["recorded_at"]:
        raise ValidationError("finding.recorded_at cannot change")
    for field in APPEND_ONLY_FINDING_FIELDS:
        before = current.get(field) or []
        if updated[field][: len(before)] != before:
            raise ValidationError(f"finding.{field} is append-only; existing entries cannot be removed or changed")
    if current["status"] != "candidate":
        for field in SETTLED_FINDING_FIELDS:
            if updated.get(field) != current.get(field):
                raise ValidationError(
                    f"finding.{field} is fixed once a finding is {current['status']}; record new observations as attempts"
                )


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

    def session_lock(self, session_id: str):
        """Serialize writers to one session; every read-modify-write holds it."""

        return exclusive_lock(self.session_path(session_id).with_name(".session.lock"))

    def create_session(self, input_payload: dict[str, Any]) -> dict[str, Any]:
        self.load_manifest()
        session = normalize_session(input_payload)
        path = self.session_path(session["id"])
        with self.session_lock(session["id"]):
            if path.exists():
                raise ValidationError(f"session already exists: {session['id']}")
            self._validate_continuation(session)
            atomic_write_json(path, session)
        return session

    def _validate_continuation(
        self,
        session: dict[str, Any],
        sessions_by_id: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        continuation = session.get("continuation_of")
        if continuation is None:
            return
        source_id = continuation["session_id"]
        if source_id == session["id"]:
            raise ValidationError("a session cannot continue itself")
        if sessions_by_id is None:
            source = self.load_session(source_id)
        else:
            source = sessions_by_id.get(source_id)
            if source is None:
                raise ValidationError(f"continuation references unknown session: {source_id}")
        if source["status"] not in TERMINAL_SESSION_STATUSES:
            raise ValidationError("continuation source session must be terminal")
        finding_id = continuation.get("finding_id")
        if finding_id is not None and finding_id not in {item["id"] for item in source["findings"]}:
            raise ValidationError(f"continuation references unknown finding: {finding_id}")

    def load_session(self, session_id: str) -> dict[str, Any]:
        payload = read_json(self.session_path(session_id))
        validate_session(payload)
        return payload

    def save_session(self, payload: dict[str, Any]) -> None:
        validate_session(payload)
        atomic_write_json(self.session_path(payload["id"]), payload)

    def add_attempt(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._add_attempt(session_id, input_payload)

    def _add_attempt(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
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
        with self.session_lock(session_id):
            return self._add_finding(session_id, input_payload)

    def _add_finding(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
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
        with self.session_lock(session_id):
            return self._update_finding(session_id, finding_id, input_payload)

    def _update_finding(self, session_id: str, finding_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
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
        _check_finding_history(current, updated)
        unknown_attempts = sorted(set(updated["attempt_ids"]) - {item["id"] for item in session["attempts"]})
        if unknown_attempts:
            raise ValidationError(f"finding references unknown attempts: {', '.join(unknown_attempts)}")
        session["findings"][finding_index] = updated
        self.save_session(session)
        return updated

    def close_session(self, session_id: str, status: str, decision: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._close_session(session_id, status, decision)

    def _close_session(self, session_id: str, status: str, decision: dict[str, Any]) -> dict[str, Any]:
        session = self.load_session(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("session is already terminal")
        if status not in TERMINAL_SESSION_STATUSES:
            raise ValidationError("close status must be completed or blocked")
        session["status"] = status
        session["closed_at"] = utc_now()
        session["decision"] = decision
        attempted_charters = {attempt["charter_id"] for attempt in session["attempts"]}
        for charter in session["charters"]:
            if charter["status"] in {"planned", "running"}:
                if status == "completed" and charter["id"] in attempted_charters:
                    charter["status"] = "completed"
                else:
                    charter["status"] = "blocked"
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
        sessions_by_id = {session["id"]: session for session in sessions}
        for session in sessions:
            self._validate_continuation(session, sessions_by_id)
        return {
            "sessions": len(sessions),
            "attempts": sum(len(item["attempts"]) for item in sessions),
            "findings": sum(len(item["findings"]) for item in sessions),
        }
