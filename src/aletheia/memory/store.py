"""Longitudinal memory store with SQLite persistence and JSONL fallback.

Privacy commitments:
- Per-user isolation (entries are scoped by user_id)
- No cross-user learning from stored memory
- Auditable: every entry has a creation timestamp and review trail
- Deletable: by entry_id, by tag, or full wipe (irreversible)
"""
from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import structlog

from ..core.config import get_settings
from ..core.types import EpistemicStatus, HypothesisStatus
from .entry import MemoryEntry, MemoryKind

log = structlog.get_logger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL,
    epistemic_status TEXT NOT NULL,
    hypothesis_status TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence TEXT NOT NULL,        -- JSON array
    counterevidence TEXT NOT NULL, -- JSON array
    tags TEXT NOT NULL,            -- JSON array
    superseded_by TEXT,
    created_at TEXT NOT NULL,
    last_reviewed TEXT NOT NULL,
    session_ids TEXT NOT NULL      -- JSON array
);
CREATE INDEX IF NOT EXISTS idx_memory_user ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_user_kind ON memory_entries(user_id, kind);
CREATE INDEX IF NOT EXISTS idx_memory_user_status ON memory_entries(user_id, hypothesis_status);
"""


class LongitudinalMemory:
    """Privacy-first longitudinal memory with SQLite persistence.

    Falls back to in-memory storage when SQLite is unavailable.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        settings = get_settings()
        self.db_path = Path(db_path) if db_path else Path(settings.db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._in_memory: list[MemoryEntry] = []
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        try:
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,  # autocommit
            )
            self._conn.executescript(_SCHEMA)
            log.info("memory.db.initialized", path=str(self.db_path))
        except sqlite3.Error as e:
            log.warning("memory.db.fallback_to_in_memory", error=str(e))
            self._conn = None

    # ── writes ────────────────────────────────────────────────

    def add(
        self,
        entry: MemoryEntry | None = None,
        *,
        kind: MemoryKind | None = None,
        text: str | None = None,
        user_id: str = "anonymous",
        epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION,
        confidence: float = 0.4,
        evidence: list[str] | None = None,
        tags: list[str] | None = None,
        session_id: str | None = None,
    ) -> MemoryEntry:
        """Add an entry. Either pass a MemoryEntry or construct one inline."""
        if entry is None:
            if kind is None or text is None:
                raise ValueError("Either pass a MemoryEntry or provide kind+text")
            entry = MemoryEntry(
                id=f"mem_{uuid.uuid4().hex[:12]}",
                user_id=user_id,
                kind=kind,
                text=text,
                epistemic_status=epistemic_status,
                confidence=confidence,
                evidence=evidence or [],
                tags=tags or [],
                session_ids=[session_id] if session_id else [],
            )
        else:
            entry.user_id = entry.user_id or user_id
            if session_id and session_id not in entry.session_ids:
                entry.session_ids.append(session_id)

        self._persist(entry)
        return entry

    def update(self, entry: MemoryEntry) -> None:
        """Persist changes to an existing entry."""
        entry.last_reviewed = datetime.now(timezone.utc)
        self._persist(entry)

    def _persist(self, entry: MemoryEntry) -> None:
        if self._conn is None:
            with self._lock:
                # Replace if exists, else append
                self._in_memory = [e for e in self._in_memory if e.id != entry.id]
                self._in_memory.append(entry)
            return

        with self._lock:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO memory_entries
                (id, user_id, kind, text, epistemic_status, hypothesis_status,
                 confidence, evidence, counterevidence, tags, superseded_by,
                 created_at, last_reviewed, session_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.user_id,
                    entry.kind,
                    entry.text,
                    entry.epistemic_status.value,
                    entry.hypothesis_status.value,
                    entry.confidence,
                    json.dumps(entry.evidence),
                    json.dumps(entry.counterevidence),
                    json.dumps(entry.tags),
                    entry.superseded_by,
                    entry.created_at.isoformat(),
                    entry.last_reviewed.isoformat(),
                    json.dumps(entry.session_ids),
                ),
            )

    # ── reads ─────────────────────────────────────────────────

    def get(self, entry_id: str) -> MemoryEntry | None:
        rows = self._query("SELECT * FROM memory_entries WHERE id = ?", (entry_id,))
        return rows[0] if rows else None

    def all_for_user(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self._query(
            "SELECT * FROM memory_entries WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )

    def by_kind(self, user_id: str, kind: MemoryKind) -> list[MemoryEntry]:
        return self._query(
            "SELECT * FROM memory_entries WHERE user_id = ? AND kind = ? ORDER BY created_at DESC",
            (user_id, kind),
        )

    def active_hypotheses(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self._query(
            "SELECT * FROM memory_entries WHERE user_id = ? AND kind = 'hypothesis' AND hypothesis_status = 'active' ORDER BY last_reviewed DESC",
            (user_id,),
        )

    def all_hypotheses(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self._query(
            "SELECT * FROM memory_entries WHERE user_id = ? AND kind = 'hypothesis' ORDER BY last_reviewed DESC",
            (user_id,),
        )

    def declared_values(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self.by_kind(user_id, "declared_value")

    def decisions(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self.by_kind(user_id, "decision")

    def experiments(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self.by_kind(user_id, "experiment")

    def patterns(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self.by_kind(user_id, "pattern")

    def themes(self, user_id: str = "anonymous") -> list[MemoryEntry]:
        return self.by_kind(user_id, "theme")

    def by_tag(self, user_id: str, tag: str) -> list[MemoryEntry]:
        all_entries = self.all_for_user(user_id)
        return [e for e in all_entries if tag in e.tags]

    def search(self, user_id: str, query: str) -> list[MemoryEntry]:
        """Simple substring search across entry text. (Vector search is in wisdom/.)"""
        q = f"%{query.lower()}%"
        return self._query(
            "SELECT * FROM memory_entries WHERE user_id = ? AND LOWER(text) LIKE ? ORDER BY last_reviewed DESC",
            (user_id, q),
        )

    # ── deletion ──────────────────────────────────────────────

    def delete(self, entry_id: str) -> bool:
        """Delete a single entry. Irreversible."""
        if self._conn is None:
            with self._lock:
                before = len(self._in_memory)
                self._in_memory = [e for e in self._in_memory if e.id != entry_id]
                return len(self._in_memory) < before
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM memory_entries WHERE id = ?", (entry_id,)
            )
            return cur.rowcount > 0

    def delete_by_tag(self, user_id: str, tag: str) -> int:
        """Delete all entries with a given tag. Returns count deleted."""
        entries = self.by_tag(user_id, tag)
        for e in entries:
            self.delete(e.id)
        return len(entries)

    def wipe(self, user_id: str) -> int:
        """Delete ALL entries for a user. Irreversible. Returns count deleted."""
        count = len(self.all_for_user(user_id))
        if self._conn is None:
            with self._lock:
                self._in_memory = [e for e in self._in_memory if e.user_id != user_id]
        else:
            with self._lock:
                self._conn.execute(
                    "DELETE FROM memory_entries WHERE user_id = ?", (user_id,)
                )
        log.info("memory.wiped", user_id=user_id, count=count)
        return count

    def export(self, user_id: str = "anonymous") -> list[dict]:
        """Export all entries as JSON-serializable dicts (GDPR-style export)."""
        return [e.model_dump(mode="json") for e in self.all_for_user(user_id)]

    # ── internals ─────────────────────────────────────────────

    def _query(self, sql: str, params: tuple) -> list[MemoryEntry]:
        if self._conn is None:
            # In-memory fallback
            if "WHERE user_id = ?" in sql:
                user_id = params[0]
                rows = [e for e in self._in_memory if e.user_id == user_id]
            else:
                rows = list(self._in_memory)
            # Apply kind filter if present
            if "AND kind = ?" in sql and len(params) >= 2:
                kind = params[1]
                rows = [e for e in rows if e.kind == kind]
            # Apply hypothesis_status filter if present
            if "AND hypothesis_status = 'active'" in sql:
                rows = [e for e in rows if e.hypothesis_status == HypothesisStatus.ACTIVE]
            # Apply LIKE filter if present
            if "LOWER(text) LIKE ?" in sql and len(params) >= 2:
                q = params[1].strip("%").lower()
                rows = [e for e in rows if q in e.text.lower()]
            # Sort by created_at desc
            rows.sort(key=lambda e: e.created_at, reverse=True)
            return rows

        with self._lock:
            cur = self._conn.execute(sql, params)
            cols = [d[0] for d in cur.description]
            out: list[MemoryEntry] = []
            for row in cur.fetchall():
                d = dict(zip(cols, row, strict=True))
                out.append(self._row_to_entry(d))
            return out

    @staticmethod
    def _row_to_entry(d: dict) -> MemoryEntry:
        return MemoryEntry(
            id=d["id"],
            user_id=d["user_id"],
            kind=d["kind"],
            text=d["text"],
            epistemic_status=EpistemicStatus(d["epistemic_status"]),
            hypothesis_status=HypothesisStatus(d["hypothesis_status"]),
            confidence=float(d["confidence"]),
            evidence=json.loads(d["evidence"]),
            counterevidence=json.loads(d["counterevidence"]),
            tags=json.loads(d["tags"]),
            superseded_by=d.get("superseded_by"),
            created_at=datetime.fromisoformat(d["created_at"]),
            last_reviewed=datetime.fromisoformat(d["last_reviewed"]),
            session_ids=json.loads(d["session_ids"]),
        )

    def stats(self, user_id: str = "anonymous") -> dict[str, int]:
        entries = self.all_for_user(user_id)
        stats: dict[str, int] = {
            "total": len(entries),
            "active_hypotheses": sum(1 for e in entries if e.kind == "hypothesis" and e.is_active()),
            "weakened_hypotheses": sum(
                1 for e in entries if e.hypothesis_status == HypothesisStatus.WEAKENED
            ),
            "rejected_hypotheses": sum(
                1 for e in entries if e.hypothesis_status == HypothesisStatus.REJECTED
            ),
            "superseded_hypotheses": sum(
                1 for e in entries if e.hypothesis_status == HypothesisStatus.SUPERSEDED
            ),
        }
        for kind in (
            "declared_value", "decision", "experiment", "hypothesis",
            "pattern", "theme", "question", "perspective_change",
        ):
            stats[kind] = sum(1 for e in entries if e.kind == kind)
        return stats

    def __repr__(self) -> str:
        return f"LongitudinalMemory(db_path={self.db_path!r})"


# ── Module-level singleton ────────────────────────────────────
_memory_instance: LongitudinalMemory | None = None


def get_memory() -> LongitudinalMemory:
    """Return a process-wide LongitudinalMemory singleton."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LongitudinalMemory()
    return _memory_instance


__all__ = ["LongitudinalMemory", "get_memory"]
