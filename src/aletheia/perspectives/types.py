"""Perspective types."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..core.types import EpistemicStatus, SourceCitation, WisdomClaim

PerspectiveName = Literal[
    "Stoic",
    "Zen",
    "Sufi",
    "Taoist",
    "Existential",
    "Vedantic",
    "Christian Mystical",
    "Kabbalistic",
    "Psychological",
    "Scientific",
    "Practical",
    "Ethical",
]

PerspectiveCategory = Literal[
    "philosophy",
    "mysticism",
    "psychology",
    "science",
    "practical",
    "ethical",
]


class Perspective(BaseModel):
    """A single perspective on an issue.

    Every perspective MUST be clearly labeled and epistemically marked.
    Philosophical/spiritual perspectives are always PHILOSOPHICAL-VIEW,
    never FACT.
    """

    name: PerspectiveName
    category: PerspectiveCategory
    tradition_id: str | None = None
    text: str
    epistemic_status: EpistemicStatus = EpistemicStatus.PHILOSOPHICAL_VIEW
    citation: SourceCitation | None = None
    supporting_claims: list[WisdomClaim] = Field(default_factory=list)
    counter_perspectives: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def summary(self) -> str:
        return f"[{self.name}] {self.text[:120]}..."


class PerspectiveView(BaseModel):
    """The full multi-perspective view of a statement."""

    statement: str
    perspectives: list[Perspective] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def by_name(self, name: PerspectiveName) -> Perspective | None:
        for p in self.perspectives:
            if p.name == name:
                return p
        return None


__all__ = ["Perspective", "PerspectiveCategory", "PerspectiveName", "PerspectiveView"]
