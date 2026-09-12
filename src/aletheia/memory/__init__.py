"""Longitudinal Memory — privacy-first semantic memory.

MVP scope note: This module is a typed interface stub. Full implementation
(privacy-preserving memory store, periodic Personal Reflection Reports) is
planned for v0.3. See `docs/memory-model.md` for the design.

Critical principle: memory ≠ truth. Stored entries are revisable hypotheses
about the user, not facts about them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..core.types import EpistemicStatus, HypothesisStatus


@dataclass
class MemoryEntry:
    """A single longitudinal memory entry. NOT a fact about the user."""

    id: str
    kind: str  # "declared_value", "decision", "experiment", "hypothesis", "pattern"
    text: str
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION
    hypothesis_status: HypothesisStatus = HypothesisStatus.ACTIVE
    evidence: list[str] = field(default_factory=list)
    counterevidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def revise(self, new_status: HypothesisStatus, note: str = "") -> None:
        """Mark this entry as revised. Updates last_reviewed."""
        self.hypothesis_status = new_status
        self.last_reviewed = datetime.now(timezone.utc)
        if note:
            self.counterevidence.append(note)


@dataclass
class LongitudinalMemory:
    """Stub memory store. Real implementation will persist to SQLite."""

    entries: list[MemoryEntry] = field(default_factory=list)

    def add(self, entry: MemoryEntry) -> None:
        self.entries.append(entry)

    def get(self, entry_id: str) -> MemoryEntry | None:
        for e in self.entries:
            if e.id == entry_id:
                return e
        return None

    def active_hypotheses(self) -> list[MemoryEntry]:
        return [e for e in self.entries if e.hypothesis_status == HypothesisStatus.ACTIVE]

    def reflection_report(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Not yet implemented. Returns a stub report."""
        return {
            "recurring_themes": [],
            "unresolved_questions": [],
            "value_behavior_tensions": [],
            "hypotheses_gained_evidence": [],
            "hypotheses_lost_evidence": [],
            "completed_experiments": [],
            "changes_in_perspective": [],
            "note": "Longitudinal reflection reports are not yet implemented in v0.1.",
        }


__all__ = ["LongitudinalMemory", "MemoryEntry"]
