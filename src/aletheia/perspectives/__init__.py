"""Multi-Perspective Engine — view an issue through multiple lenses.

MVP scope note: This module is a typed interface stub. Full implementation
(Stoic, Zen, Sufi, Taoist, Existential, Psychological, Scientific, Practical,
Ethical lenses) is planned for v0.2. See `docs/architecture.md`.

The engine MUST:
- Clearly label each perspective
- Never present philosophical/spiritual traditions as scientific facts
- Never fabricate quotations
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..core.types import EpistemicStatus, SourceCitation


@dataclass
class Perspective:
    """A single perspective on an issue."""

    name: str  # "Stoic", "Zen", "Sufi", etc.
    category: str  # "philosophy", "mysticism", "science", etc.
    text: str
    epistemic_status: EpistemicStatus = EpistemicStatus.PHILOSOPHICAL_VIEW
    citation: SourceCitation | None = None
    counter_perspectives: list[str] = field(default_factory=list)


@dataclass
class MultiPerspectiveEngine:
    """Stub engine. Real implementation will use the Wisdom Graph."""

    available_perspectives: list[str] = field(default_factory=lambda: [
        "Stoic", "Zen", "Sufi", "Taoist", "Existential",
        "Psychological", "Scientific", "Practical", "Ethical",
    ])

    def view_through(self, perspective_name: str, statement: str) -> Perspective:
        """Not yet implemented. Returns a stub Perspective."""
        return Perspective(
            name=perspective_name,
            category="stub",
            text=(
                f"[PHILOSOPHICAL-VIEW] The {perspective_name} perspective on this issue "
                "is not yet implemented in v0.1. The full multi-perspective engine is "
                "planned for v0.2 and will retrieve attributed, sourced views from the Wisdom Graph."
            ),
            epistemic_status=EpistemicStatus.PHILOSOPHICAL_VIEW,
        )

    def all_perspectives(self, statement: str) -> list[Perspective]:
        """Return stub perspectives for all available lenses."""
        return [self.view_through(p, statement) for p in self.available_perspectives]


__all__ = ["MultiPerspectiveEngine", "Perspective"]
