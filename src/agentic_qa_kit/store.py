from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .model import (
    FINDING_STATUSES,
    SESSION_SCHEMA_VERSION,
    TERMINAL_SESSION_STATUSES,
    ValidationError,
    check_obligation_links,
    normalize_attempt,
    normalize_finding,
    normalize_session,
    read_json,
    utc_now,
    validate_manifest,
    validate_session,
)
from .receipts import append_receipt, chain_problems, file_digest, integrity


FINDING_TRANSITIONS = {
    "candidate": FINDING_STATUSES,
    "confirmed": {"confirmed"},
    "not-reproduced": {"not-reproduced"},
    "dismissed": {"dismissed"},
}

# History a finding accumulates. Entries may be appended, never removed or
# rewritten, so an update cannot erase evidence that was already recorded.
APPEND_ONLY_FINDING_FIELDS = ("attempt_ids", "evidence", "limitations")
# What was observed and what it means. Fixed once a finding leaves `candidate`;
# a later observation belongs in a new attempt or a continuation, not in an edit.
SETTLED_FINDING_FIELDS = ("title", "summary", "expected", "actual", "oracle", "severity", "acceptance_criteria")
# `reproduction.attempts` stays out: it counts `attempt_ids`, which may grow.
SETTLED_REPRODUCTION_FIELDS = ("preconditions", "steps", "reproducibility")


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
        for field in SETTLED_REPRODUCTION_FIELDS:
            if updated["reproduction"].get(field) != current["reproduction"].get(field):
                raise ValidationError(
                    f"finding.reproduction.{field} is fixed once a finding is {current['status']}; "
                    "record new observations as attempts"
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


DEFAULT_EVIDENCE_ROOT = ".agentic-qa/sessions"


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
                "evidence_root": DEFAULT_EVIDENCE_ROOT,
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

    @property
    def sessions_root(self) -> Path:
        """Where sessions live: the manifest's `defaults.evidence_root`.

        Before a manifest exists the default applies, so a read of an empty
        ledger still works. A root that resolves outside the repository, for
        example through a symlink, is refused.
        """

        relative = DEFAULT_EVIDENCE_ROOT
        if self.manifest_path.exists():
            relative = self.load_manifest()["defaults"]["evidence_root"]
        resolved = (self.root / relative).resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise ValidationError("manifest.defaults.evidence_root must stay inside the target repository")
        return resolved

    def session_path(self, session_id: str) -> Path:
        session_id = self._session_id(session_id)
        return self.sessions_root / session_id / "session.json"

    def session_lock(self, session_id: str):
        """Serialize writers to one session; every read-modify-write holds it."""

        return exclusive_lock(self.session_path(session_id).with_name(".session.lock"))

    def create_session(self, input_payload: dict[str, Any]) -> dict[str, Any]:
        self.load_manifest()
        # New sessions are always chained, whatever version the input names.
        payload = {**input_payload, "schema_version": SESSION_SCHEMA_VERSION, "receipts": []}
        session = normalize_session(payload)
        path = self.session_path(session["id"])
        with self.session_lock(session["id"]):
            if path.exists():
                raise ValidationError(f"session already exists: {session['id']}")
            self._validate_continuation(session)
            self._commit(session, "session-create", None)
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

    def _load_for_write(self, session_id: str) -> dict[str, Any]:
        """Load a session to change it, refusing one whose chain is broken.

        Sealing a new receipt over a tampered session would hide the tamper,
        so a broken session takes no further writes.
        """

        session = self.load_session(session_id)
        if session["schema_version"] == SESSION_SCHEMA_VERSION:
            problems = chain_problems(session)
            if problems:
                raise ValidationError(
                    f"session {session_id} failed its integrity check, so it takes no writes: {problems[0]}"
                )
        return session

    def evidence_file(self, location: str) -> Path | None:
        """The repository file an evidence location names, or None.

        Only a relative location that resolves to a regular file inside the
        repository qualifies; a URL, an absolute path, a directory or a path
        that escapes the repository is left alone.
        """

        if "://" in location or Path(location).is_absolute():
            return None
        resolved = (self.root / location).resolve()
        if self.root not in resolved.parents or not resolved.is_file():
            return None
        return resolved

    def _seal_evidence(self, entries: list[dict[str, Any]], where: str) -> None:
        """Digest new evidence files, and check a digest the caller supplied.

        A `sha256:` digest is compared with the file; a mismatch is refused,
        because it records evidence that is not the file on disk. Any other
        digest form is kept as declared and is not checked.
        """

        for index, entry in enumerate(entries):
            path = self.evidence_file(entry["location"])
            if path is None:
                continue
            actual = file_digest(path)
            declared = entry.get("digest")
            if declared is None:
                entry["digest"] = actual
            elif declared.startswith("sha256:") and declared != actual:
                raise ValidationError(
                    f"{where}[{index}].digest does not match the file at {entry['location']}"
                )

    def evidence_problems(self, session: dict[str, Any]) -> tuple[list[str], int, int]:
        """Changed evidence files, and counts of verified and missing ones."""

        problems: list[str] = []
        verified = missing = 0
        records = [("attempt", item) for item in session["attempts"]]
        records += [("finding", item) for item in session["findings"]]
        for kind, record in records:
            for entry in record.get("evidence") or []:
                declared = entry.get("digest")
                if not declared or not declared.startswith("sha256:"):
                    continue
                path = self.evidence_file(entry["location"])
                if path is None:
                    missing += 1
                elif file_digest(path) != declared:
                    problems.append(f"{kind} {record['id']} evidence {entry['location']} changed after it was recorded")
                else:
                    verified += 1
        return problems, verified, missing

    def _commit(self, session: dict[str, Any], op: str, subject: str | None) -> None:
        if session["schema_version"] == SESSION_SCHEMA_VERSION:
            append_receipt(session, op, subject, utc_now())
        self.save_session(session)

    def migrate_session(self, session_id: str) -> dict[str, Any]:
        """Seal a schema-version-1 session as version 2 with a `migrate` receipt.

        The receipt vouches only for the session as it stands now; nothing
        before it was chained, and the migration says so by its operation.
        """

        with self.session_lock(session_id):
            session = self.load_session(session_id)
            if session["schema_version"] != 1:
                raise ValidationError(f"session {session_id} is already at schema version {session['schema_version']}")
            session["schema_version"] = SESSION_SCHEMA_VERSION
            session["receipts"] = []
            self._commit(session, "migrate", None)
        return session

    def add_attempt(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._add_attempt(session_id, input_payload)

    def _add_attempt(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self._load_for_write(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("cannot add an attempt to a terminal session")
        attempt = normalize_attempt(input_payload)
        self._seal_evidence(attempt["evidence"], "attempt.evidence")
        charter_ids = {charter["id"] for charter in session["charters"]}
        if attempt["charter_id"] not in charter_ids:
            raise ValidationError(f"unknown charter ID: {attempt['charter_id']}")
        check_obligation_links(attempt, session["charters"])
        if attempt["id"] in {item["id"] for item in session["attempts"]}:
            raise ValidationError(f"attempt already exists: {attempt['id']}")
        session["attempts"].append(attempt)
        if session["status"] == "planned":
            session["status"] = "running"
        for charter in session["charters"]:
            if charter["id"] == attempt["charter_id"] and charter["status"] == "planned":
                charter["status"] = "running"
        self._commit(session, "attempt-add", attempt["id"])
        return attempt

    def add_finding(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._add_finding(session_id, input_payload)

    def _add_finding(self, session_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self._load_for_write(session_id)
        if session["status"] in TERMINAL_SESSION_STATUSES:
            raise ValidationError("cannot add a finding to a terminal session")
        finding = normalize_finding(input_payload)
        self._seal_evidence(finding["evidence"], "finding.evidence")
        if finding["id"] in {item["id"] for item in session["findings"]}:
            raise ValidationError(f"finding already exists: {finding['id']}")
        unknown_attempts = sorted(set(finding["attempt_ids"]) - {item["id"] for item in session["attempts"]})
        if unknown_attempts:
            raise ValidationError(f"finding references unknown attempts: {', '.join(unknown_attempts)}")
        session["findings"].append(finding)
        self._commit(session, "finding-add", finding["id"])
        return finding

    def update_finding(self, session_id: str, finding_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._update_finding(session_id, finding_id, input_payload)

    def _update_finding(self, session_id: str, finding_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
        session = self._load_for_write(session_id)
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
        recorded = current.get("evidence") or []
        for before, entry in zip(recorded, updated["evidence"]):
            # A caller restating an earlier entry need not repeat its digest.
            if "digest" in before and "digest" not in entry and {**entry, "digest": before["digest"]} == before:
                entry["digest"] = before["digest"]
        self._seal_evidence(updated["evidence"][len(recorded):], "finding.evidence")
        if updated["status"] not in FINDING_TRANSITIONS[current["status"]]:
            raise ValidationError(f"invalid finding transition: {current['status']} -> {updated['status']}")
        _check_finding_history(current, updated)
        unknown_attempts = sorted(set(updated["attempt_ids"]) - {item["id"] for item in session["attempts"]})
        if unknown_attempts:
            raise ValidationError(f"finding references unknown attempts: {', '.join(unknown_attempts)}")
        session["findings"][finding_index] = updated
        self._commit(session, "finding-update", finding_id)
        return updated

    def close_session(self, session_id: str, status: str, decision: dict[str, Any]) -> dict[str, Any]:
        with self.session_lock(session_id):
            return self._close_session(session_id, status, decision)

    def _close_session(self, session_id: str, status: str, decision: dict[str, Any]) -> dict[str, Any]:
        session = self._load_for_write(session_id)
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
        self._commit(session, "session-close", None)
        return session

    def list_sessions(self) -> list[dict[str, Any]]:
        sessions_root = self.sessions_root
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
        broken = {
            session["id"]: chain_problems(session)
            for session in sessions
            if integrity(session) == "broken"
        }
        changed: list[str] = []
        verified = missing = 0
        for session in sessions:
            problems, ok, absent = self.evidence_problems(session)
            changed.extend(f"{session['id']}: {problem}" for problem in problems)
            verified += ok
            missing += absent
        if broken:
            details = "; ".join(f"{sid}: {problems[0]}" for sid, problems in sorted(broken.items()))
            raise ValidationError(f"integrity check failed for {len(broken)} session(s): {details}")
        if changed:
            raise ValidationError(f"{len(changed)} evidence file(s) changed after they were recorded: {changed[0]}")
        return {
            "sessions": len(sessions),
            "chained": sum(1 for item in sessions if integrity(item) == "chained"),
            "unchained": sum(1 for item in sessions if integrity(item) == "unchained"),
            "attempts": sum(len(item["attempts"]) for item in sessions),
            "findings": sum(len(item["findings"]) for item in sessions),
            "evidence_verified": verified,
            "evidence_missing": missing,
        }
