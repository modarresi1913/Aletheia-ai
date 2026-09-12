"""Contradiction Engine — tracks recurring value/behavior tensions.

MVP scope note: This module is a typed interface stub. Full implementation
(longitudinal contradiction tracking, value/behavior coherence scoring) is
planned for v0.2. See `docs/architecture.md` for the design.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.types import HypothesisStatus


@dataclass
class Contradiction:
    """A tension between two positions held by the same user."""

    id: str
    description: str
    side_a: str
    side_b: str
    evidence_a: list[str] = field(default_factory=list)
    evidence_b: list[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    notes: list[str] = field(default_factory=list)


@dataclass
class ContradictionEngine:
    """Stub engine. Real implementation will track longitudinal memory."""

    contradictions: list[Contradiction] = field(default_factory=list)

    def detect(self, *args: Any, **kwargs: Any) -> list[Contradiction]:
        """Not yet implemented. Returns an empty list."""
        return []

    def render(self, contradiction: Contradiction) -> str:
        lines = [
            f"Contradiction: {contradiction.description}",
            f"  side A: {contradiction.side_a}  (evidence: {len(contradiction.evidence_a)})",
            f"  side B: {contradiction.side_b}  (evidence: {len(contradiction.evidence_b)})",
            f"  status: {contradiction.status.value}",
        ]
        if contradiction.notes:
            lines.append("  notes:")
            for n in contradiction.notes:
                lines.append(f"    - {n}")
        return "\n".join(lines)


__all__ = ["Contradiction", "ContradictionEngine"]
