"""Contradiction Engine — coordinates detection, storage, and presentation.

The engine NEVER shames the user. Contradictions are surfaced as one possible
reading, with multiple interpretations offered. The user can always reject the
interpretation.
"""
from __future__ import annotations

import structlog

from ..memory.store import LongitudinalMemory
from .detector import ContradictionDetector
from .types import Contradiction, ContradictionDetection

log = structlog.get_logger(__name__)


class ContradictionEngine:
    """Coordinates contradiction detection and presentation."""

    def __init__(
        self,
        memory: LongitudinalMemory | None = None,
        detector: ContradictionDetector | None = None,
    ) -> None:
        self.memory = memory or LongitudinalMemory()
        self.detector = detector or ContradictionDetector(self.memory)
        self._cache: dict[str, Contradiction] = {}

    def detect(
        self,
        user_id: str = "anonymous",
        current_statement: str | None = None,
    ) -> ContradictionDetection:
        """Detect contradictions for a user, optionally including the current statement."""
        return self.detector.detect_all(user_id, current_statement)

    def get_active(self, user_id: str = "anonymous") -> list[Contradiction]:
        """Return all active contradictions for a user."""
        return [
            c for c in self._cache.values()
            if c.user_id == user_id and c.is_active()
        ]

    def store(self, contradiction: Contradiction) -> None:
        """Cache a contradiction for later retrieval."""
        self._cache[contradiction.id] = contradiction

    def render(self, contradiction: Contradiction) -> str:
        """Render a contradiction as a readable, non-shaming text block."""
        lines = [
            "POSSIBLE TENSION DETECTED",
            "─" * 60,
            contradiction.description,
            "",
            f"  side A ({contradiction.side_a_kind}): {contradiction.side_a}",
            f"  side B ({contradiction.side_b_kind}): {contradiction.side_b}",
            "",
            "POSSIBLE INTERPRETATIONS (not judgments):",
        ]
        for i, interp in enumerate(contradiction.interpretations, 1):
            lines.append(f"  {i}. {interp}")
        lines += [
            "",
            f"[{contradiction.epistemic_status.value}] "
            "This is an interpretation, not a conclusion. You can reject it.",
        ]
        return "\n".join(lines)

    def render_detection(self, detection: ContradictionDetection) -> str:
        """Render the full output of a detection pass."""
        if not detection.contradictions:
            return (
                "No active contradictions detected.\n"
                "Note: absence of detected contradiction does not imply absence of tension; "
                "the heuristics are conservative."
            )
        lines = [f"Detected {len(detection.contradictions)} possible tension(s):\n"]
        for i, c in enumerate(detection.contradictions, 1):
            lines.append(f"── Tension {i} ──────────────────────────────────")
            lines.append(self.render(c))
            lines.append("")
        if detection.notes:
            lines.append("Notes:")
            for n in detection.notes:
                lines.append(f"  - {n}")
        return "\n".join(lines)


__all__ = ["ContradictionEngine"]
