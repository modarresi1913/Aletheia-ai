"""Epistemic label utilities.

The labels form an ordered lattice from strongest (FACT) to weakest (UNKNOWN).
A claim may only move to a stronger status when explicit evidence justifies it.
"""
from __future__ import annotations

from ..core.types import EpistemicStatus

# Ordered from strongest to weakest
_RANK: dict[EpistemicStatus, int] = {
    EpistemicStatus.FACT: 7,
    EpistemicStatus.EVIDENCE_SUPPORTED: 6,
    EpistemicStatus.PLAUSIBLE: 5,
    EpistemicStatus.INTERPRETATION: 4,
    EpistemicStatus.PHILOSOPHICAL_VIEW: 3,
    EpistemicStatus.SPECULATION: 2,
    EpistemicStatus.UNKNOWN: 1,
}


def status_rank(status: EpistemicStatus) -> int:
    """Higher = stronger evidence. UNKNOWN = 1, FACT = 7."""
    return _RANK[status]


def label_strength(status: EpistemicStatus) -> str:
    """Human-readable strength category."""
    r = status_rank(status)
    if r >= 6:
        return "strong"
    if r >= 4:
        return "moderate"
    return "weak"


def can_promote_to(current: EpistemicStatus, target: EpistemicStatus) -> bool:
    """Whether a claim may be promoted from `current` to `target`.

    Promotion is allowed only to a stronger status, never to a weaker one
    (that would be a demotion). Demotion is allowed but logged.
    """
    return status_rank(target) > status_rank(current)


__all__ = ["can_promote_to", "label_strength", "status_rank"]
