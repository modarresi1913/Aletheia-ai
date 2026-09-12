"""Memory entry — a single revisable hypothesis about the user.

Critical: a MemoryEntry is NEVER a fact about the user. It is a structured
hypothesis that may be revised, weakened, or rejected as new evidence appears.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ..core.types import EpistemicStatus, HypothesisStatus

MemoryKind = Literal[
    "declared_value",      # what the user says matters to them
    "decision",            # a concrete commitment
    "experiment",          # a tracked life experiment
    "hypothesis",          # an interpretive hypothesis
    "pattern",             # an observed regularity across sessions
    "theme",               # a recurring topic
    "question",            # an unresolved question
    "perspective_change",  # a documented shift in the user's view
]


class MemoryEntry(BaseModel):
    """A single longitudinal memory entry. NOT a fact about the user."""

    id: str
    user_id: str = Field(default="anonymous")
    kind: MemoryKind
    text: str
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION
    hypothesis_status: HypothesisStatus = HypothesisStatus.ACTIVE
    confidence: float = Field(default=0.4, ge=0.0, le=0.94)
    evidence: list[str] = Field(default_factory=list)
    counterevidence: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    superseded_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_ids: list[str] = Field(default_factory=list)

    def revise(
        self,
        new_status: HypothesisStatus,
        note: str = "",
        evidence: str | None = None,
    ) -> None:
        """Mark this entry as revised. Updates last_reviewed and appends evidence."""
        self.hypothesis_status = new_status
        self.last_reviewed = datetime.now(timezone.utc)
        if note:
            if new_status in (HypothesisStatus.WEAKENED, HypothesisStatus.REJECTED, HypothesisStatus.SUPERSEDED):
                self.counterevidence.append(note)
            else:
                self.evidence.append(note)
        if evidence:
            self.evidence.append(evidence)

    def supersede(self, new_entry_id: str, note: str = "") -> None:
        """Mark this entry as superseded by a newer hypothesis."""
        self.hypothesis_status = HypothesisStatus.SUPERSEDED
        self.superseded_by = new_entry_id
        self.last_reviewed = datetime.now(timezone.utc)
        if note:
            self.counterevidence.append(note)

    def strengthen(self, evidence: str) -> None:
        """Add corroborating evidence."""
        self.evidence.append(evidence)
        self.last_reviewed = datetime.now(timezone.utc)

    def weaken(self, counterevidence: str) -> None:
        """Add counterevidence; may downgrade status."""
        self.counterevidence.append(counterevidence)
        self.last_reviewed = datetime.now(timezone.utc)
        if self.hypothesis_status == HypothesisStatus.ACTIVE and len(self.counterevidence) >= 2:
            self.hypothesis_status = HypothesisStatus.WEAKENED

    def is_active(self) -> bool:
        return self.hypothesis_status == HypothesisStatus.ACTIVE

    def summary(self) -> str:
        """One-line summary for reports."""
        return (
            f"[{self.kind}] {self.text} "
            f"(status={self.hypothesis_status.value}, "
            f"confidence={self.confidence:.2f}, "
            f"evidence={len(self.evidence)}, "
            f"counterevidence={len(self.counterevidence)})"
        )


__all__ = ["MemoryEntry", "MemoryKind"]
