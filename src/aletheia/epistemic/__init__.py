"""Epistemic Engine — Aletheia's defining technical feature.

Decomposes user statements into the chain:

    OBSERVATION → INTERPRETATION → EMOTION → DESIRE → FEAR → VALUE → NARRATIVE → POSSIBLE_ACTION

Every layer carries an explicit `EpistemicStatus`. The decomposition never
collapses multiple interpretations into one.
"""
from __future__ import annotations

from .decomposition import EpistemicDecomposer
from .labels import EpistemicStatus, label_strength, status_rank

__all__ = ["EpistemicDecomposer", "EpistemicStatus", "label_strength", "status_rank"]
