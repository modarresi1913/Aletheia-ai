"""Core types shared across Aletheia modules.

These types encode the project's epistemic commitments:
- Every claim carries an explicit epistemic status.
- Every observation is distinguished from interpretation.
- Every hypothesis is revisable.
- Memory is not truth.
"""
from __future__ import annotations

from .config import Settings, get_settings
from .types import (
    AletheiaResponse,
    Concept,
    Confidence,
    ConfidenceField,
    DecompositionLayer,
    EpistemicDecomposition,
    EpistemicStatus,
    EvidenceLevel,
    HumanStateEstimate,
    HumanStateSignal,
    HypothesisStatus,
    ReflectionLayer,
    ReflectionRequest,
    ReflectionResult,
    SocraticQuestion,
    SourceCitation,
    Tradition,
    WisdomClaim,
    validate_confidence,
)

__all__ = [
    "AletheiaResponse",
    # Wisdom graph
    "Concept",
    "Confidence",
    "ConfidenceField",
    # Decomposition
    "DecompositionLayer",
    "EpistemicDecomposition",
    # Epistemic system
    "EpistemicStatus",
    "EvidenceLevel",
    "HumanStateEstimate",
    # Human state
    "HumanStateSignal",
    "HypothesisStatus",
    # Reflection
    "ReflectionLayer",
    "ReflectionRequest",
    "ReflectionResult",
    # Config
    "Settings",
    # Socratic
    "SocraticQuestion",
    "SourceCitation",
    "Tradition",
    "WisdomClaim",
    "get_settings",
    "validate_confidence",
]
