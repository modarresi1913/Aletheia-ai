"""Contradiction types."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ..core.types import EpistemicStatus, HypothesisStatus

ContradictionKind = Literal[
    "value_vs_decision",       # declared value vs. recent decision
    "value_vs_pattern",        # declared value vs. observed pattern of behavior
    "stated_belief_vs_action", # explicit belief vs. action taken
    "goal_vs_behavior",        # long-term goal vs. recent behavior
    "identity_vs_action",      # self-described identity vs. action
    "intra_statement",         # contradiction within a single statement
]


class Contradiction(BaseModel):
    """A tension between two positions held by the same user.

    Never used to shame the user. Always offered as one possible reading.
    """

    id: str
    user_id: str = Field(default="anonymous")
    kind: ContradictionKind
    description: str
    side_a: str = Field(..., description="One side of the tension (e.g., declared value)")
    side_b: str = Field(..., description="The other side (e.g., recent behavior)")
    side_a_kind: str = Field(default="declared_value")
    side_b_kind: str = Field(default="decision")
    side_a_entry_id: str | None = None
    side_b_entry_id: str | None = None
    evidence_a: list[str] = Field(default_factory=list)
    evidence_b: list[str] = Field(default_factory=list)
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION
    hypothesis_status: HypothesisStatus = HypothesisStatus.ACTIVE
    interpretations: list[str] = Field(
        default_factory=list,
        description="Multiple possible interpretations of the tension",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_active(self) -> bool:
        return self.hypothesis_status == HypothesisStatus.ACTIVE

    def summary(self) -> str:
        return (
            f"[{self.kind}] {self.description}\n"
            f"  side A ({self.side_a_kind}): {self.side_a}\n"
            f"  side B ({self.side_b_kind}): {self.side_b}\n"
            f"  status: {self.hypothesis_status.value}"
        )


class ContradictionDetection(BaseModel):
    """The output of a single contradiction detection pass."""

    contradictions: list[Contradiction] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION

    def is_empty(self) -> bool:
        return not self.contradadictions if False else not self.contradictions


__all__ = ["Contradiction", "ContradictionDetection", "ContradictionKind"]
