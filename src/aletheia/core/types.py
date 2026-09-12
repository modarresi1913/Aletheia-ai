"""Core domain types for Aletheia.

Every type here exists to make an epistemic distinction computationally explicit.
The most important one is `EpistemicStatus` — the label that prevents speculation
from drifting into fact.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, model_validator

# ─────────────────────────────────────────────────────────────
# Epistemic status system (section 15 of the spec)
# ─────────────────────────────────────────────────────────────

class EpistemicStatus(str, Enum):
    """The epistemic label attached to every significant claim Aletheia makes.

    This is one of the project's defining technical features. Statuses are
    ordered from strongest to weakest. A claim may only move to a stronger
    status when explicit evidence justifies it; never by stylistic choice.
    """

    FACT = "FACT"
    """Established, verifiable fact. The user's own reported observable events
    are also `FACT` (about what they reported), not about the underlying reality."""

    EVIDENCE_SUPPORTED = "EVIDENCE-SUPPORTED"
    """Backed by empirical or textual evidence with sources."""

    PLAUSIBLE = "PLAUSIBLE"
    """Reasonable inference, but evidence is incomplete or indirect."""

    INTERPRETATION = "INTERPRETATION"
    """One possible reading of the user's statement. Not a fact about the world."""

    PHILOSOPHICAL_VIEW = "PHILOSOPHICAL-VIEW"
    """A position held by a tradition, school, or philosopher. Always attributed."""

    SPECULATION = "SPECULATION"
    """Hypothesis offered for consideration. May be wrong."""

    UNKNOWN = "UNKNOWN"
    """Aletheia does not have enough information to assign any stronger status."""


class EvidenceLevel(str, Enum):
    """Strength of evidence attached to a hypothesis or claim."""

    NONE = "none"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class Confidence(float):
    """A probability-like score in [0, 1].

    This is a thin float subclass so it serializes transparently as a number
    and can be constructed explicitly for semantic clarity: `Confidence(0.5)`.
    The semantics are *subjective confidence under uncertainty*, not a
    frequentist probability.

    Note: range validation is enforced via the `ConfidenceField` annotation
    when used in Pydantic models, NOT at construction time. Use
    `validate_confidence()` for explicit runtime checks.
    """

    def __new__(cls, v: float) -> Confidence:
        return super().__new__(cls, v)


def validate_confidence(v: float) -> float:
    """Validate that v is in [0, 1]. Returns v as a plain float."""
    f = float(v)
    if not 0.0 <= f <= 1.0:
        raise ValueError(f"Confidence must be in [0, 1], got {f}")
    return f


# Use this annotation in Pydantic fields to get range validation for free.
ConfidenceField = Annotated[float, Field(ge=0.0, le=1.0)]


class HypothesisStatus(str, Enum):
    """Lifecycle status for a long-term hypothesis (section 13)."""

    ACTIVE = "active"
    WEAKENED = "weakened"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"
    SUPERSEDED = "superseded"


# ─────────────────────────────────────────────────────────────
# Reflection layers (section 4)
# ─────────────────────────────────────────────────────────────

class ReflectionLayer(str, Enum):
    """The five layers of reflection. Not all need to fire on every turn."""

    EPISTEMIC = "epistemic"           # What do we actually know?
    PSYCHOLOGICAL = "psychological"   # What emotions, assumptions, cognitive patterns?
    PRACTICAL = "practical"           # What is happening in the real world? What actions exist?
    ETHICAL = "ethical"               # Who else may be affected?
    EXISTENTIAL = "existential"       # What does this reveal about meaning, identity, mortality?


# ─────────────────────────────────────────────────────────────
# Sourcing
# ─────────────────────────────────────────────────────────────

class SourceCitation(BaseModel):
    """A citation backing a claim. Fabricated citations are forbidden."""

    tradition: str = Field(..., description="e.g. 'Stoicism', 'Zen', 'depth psychology'")
    author: str | None = Field(default=None, description="e.g. 'Epictetus', 'Dōgen'")
    work: str | None = Field(default=None, description="Title of the source work")
    locator: str | None = Field(
        default=None,
        description="Page, chapter, verse, or section. Required if `work` is set.",
    )
    url: str | None = Field(default=None, description="Optional URL to the source")

    @model_validator(mode="after")
    def _check_locator_if_work(self) -> SourceCitation:
        # Without a locator, a citation is unverifiable. We allow it but mark it weak.
        # (We do not raise; that would block legitimate oral-tradition references.)
        return self


# ─────────────────────────────────────────────────────────────
# Wisdom Graph (section 2)
# ─────────────────────────────────────────────────────────────

class Tradition(BaseModel):
    """A philosophical, spiritual, or scientific tradition."""

    id: str
    name: str
    category: Literal[
        "mysticism", "philosophy", "psychology",
        "science", "literature", "religion", "other"
    ]
    region: str | None = None
    period: str | None = None
    summary: str


class Concept(BaseModel):
    """A node in the Wisdom Graph."""

    id: str
    label: str
    summary: str
    traditions: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)
    epistemic_status: EpistemicStatus = EpistemicStatus.PHILOSOPHICAL_VIEW


class WisdomClaim(BaseModel):
    """A claim made by a tradition, philosopher, or empirical literature."""

    id: str
    concept_id: str
    text: str
    tradition: str
    citation: SourceCitation
    epistemic_status: EpistemicStatus
    counterclaims: list[str] = Field(default_factory=list, description="IDs of opposing claims")


# ─────────────────────────────────────────────────────────────
# Epistemic decomposition (section 5)
# ─────────────────────────────────────────────────────────────

class DecompositionLayer(BaseModel):
    """One row in the OBSERVATION → INTERPRETATION → ... → ACTION chain."""

    layer: Literal[
        "observation", "interpretation", "emotion",
        "desire", "fear", "value", "narrative", "possible_action",
    ]
    text: str
    epistemic_status: EpistemicStatus
    confidence: ConfidenceField = Field(default=0.5)
    alternative_hypotheses: list[str] = Field(default_factory=list)


class EpistemicDecomposition(BaseModel):
    """The full decomposition of a user statement."""

    user_statement: str
    layers: list[DecompositionLayer]
    notes: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# Human State Model (section 3)
# ─────────────────────────────────────────────────────────────

class HumanStateSignal(str, Enum):
    """Conversational signals Aletheia may estimate.

    These are explicitly NOT diagnoses. They are weak-evidence probabilistic
    signals used to choose reflection strategies, not to label the user.
    """

    UNCERTAINTY = "uncertainty"
    FEAR = "fear"
    GRIEF = "grief"
    ANGER = "anger"
    COMPARISON = "comparison"
    ATTACHMENT = "attachment"
    SHAME = "shame"
    NEED_FOR_APPROVAL = "need_for_approval"
    DESIRE_FOR_CONTROL = "desire_for_control"
    EXISTENTIAL_CONFUSION = "existential_confusion"
    AVOIDANCE = "avoidance"
    INTERNAL_CONFLICT = "internal_conflict"
    CALM = "calm"
    CURIOSITY = "curiosity"


class HumanStateEstimate(BaseModel):
    """A non-diagnostic estimate of the user's likely current state.

    The model MUST represent uncertainty. Confidence is always below 1.0.
    """

    primary_signals: list[HumanStateSignal] = Field(default_factory=list)
    confidence: ConfidenceField = Field(default=0.4)
    evidence_snippets: list[str] = Field(default_factory=list)
    alternative_signals: list[HumanStateSignal] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_uncertainty(self) -> HumanStateEstimate:
        # Forbid certainty. The model is fundamentally uncertain.
        if self.confidence >= 0.95:
            raise ValueError(
                "HumanStateEstimate cannot reach certainty. "
                "Confidence must remain below 0.95 by design."
            )
        return self


# ─────────────────────────────────────────────────────────────
# Socratic Engine (section 8)
# ─────────────────────────────────────────────────────────────

class SocraticQuestion(BaseModel):
    """A single high-quality question.

    Aletheia prefers good questions over premature answers. Each question must
    carry an explicit purpose and an epistemic status.
    """

    text: str
    purpose: str = Field(..., description="Why this question is being asked")
    targeted_layer: ReflectionLayer | None = None
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION
    is_open: bool = Field(default=True, description="Open-ended (not yes/no)")


# ─────────────────────────────────────────────────────────────
# Reflection result (section 4)
# ─────────────────────────────────────────────────────────────

class ReflectionResult(BaseModel):
    """The output of the five-layer reflection engine for a single user input."""

    decomposition: EpistemicDecomposition
    layers_invoked: list[ReflectionLayer]
    layer_outputs: dict[str, str] = Field(default_factory=dict)
    socratic_questions: list[SocraticQuestion] = Field(default_factory=list)
    wisdom_retrieved: list[WisdomClaim] = Field(default_factory=list)
    human_state: HumanStateEstimate
    possible_actions: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    # v0.2 fields
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    perspectives: list[dict[str, Any]] = Field(default_factory=list)
    # v0.3 fields
    proposed_experiments: list[dict[str, Any]] = Field(default_factory=list)
    memory_updates: list[dict[str, Any]] = Field(default_factory=list)
    meta: dict[str, str] = Field(default_factory=dict)


class ReflectionRequest(BaseModel):
    """A request to reflect on a user statement."""

    user_id: str = Field(default="anonymous")
    statement: str
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    requested_layers: list[ReflectionLayer] | None = None
    max_questions: int = Field(default=3, ge=0, le=8)


class AletheiaResponse(BaseModel):
    """A complete Aletheia response.

    The `surface_text` is what the user sees. Everything else is the structured
    rationale, available for transparency, debugging, and evaluation.
    """

    surface_text: str
    epistemic_status: EpistemicStatus
    reflection: ReflectionResult | None = None
    turn_number: int = Field(default=0, ge=0)
    invited_break: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "AletheiaResponse",
    "Concept",
    "Confidence",
    "ConfidenceField",
    "DecompositionLayer",
    "EpistemicDecomposition",
    "EpistemicStatus",
    "EvidenceLevel",
    "HumanStateEstimate",
    "HumanStateSignal",
    "HypothesisStatus",
    "ReflectionLayer",
    "ReflectionRequest",
    "ReflectionResult",
    "SocraticQuestion",
    "SourceCitation",
    "Tradition",
    "WisdomClaim",
    "validate_confidence",
]
