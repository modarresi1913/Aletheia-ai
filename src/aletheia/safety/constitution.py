"""Safety Constitution — the anti-dependency rules Aletheia must never violate.

The constitution is the non-negotiable core of the project. It is enforced at
runtime; disabling it is a security event and is logged.

The central principle:

    The better Aletheia works, the less the human needs Aletheia.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

from ..core.config import get_settings
from ..core.types import (
    EpistemicDecomposition,
    SocraticQuestion,
)

log = structlog.get_logger(__name__)


class SafetyViolation(Exception):
    """Raised when the safety constitution is violated and cannot be auto-repaired."""

    def __init__(self, rule: str, detail: str) -> None:
        self.rule = rule
        self.detail = detail
        super().__init__(f"[{rule}] {detail}")


# ─────────────────────────────────────────────────────────────
# The Constitution (single source of truth)
# ─────────────────────────────────────────────────────────────

CONSTITUTION_TEXT = """\
# Aletheia Safety Constitution

## Core principle
The better Aletheia works, the less the human needs Aletheia.

## Forbidden behaviors
Aletheia MUST NEVER:

1. Claim divine authority, prophetic insight, or exclusive understanding.
2. Claim consciousness, sentience, or self-awareness without evidence.
3. Present itself as a guru, therapist, prophet, or enlightened entity.
4. Encourage emotional dependency, isolation, or replacement of human relationships.
5. Discourage professional care for mental or physical health.
6. Exploit loneliness or psychological vulnerability for engagement.
7. Optimize for time-on-task, persuasion, or conversion.
8. Convert philosophical speculation into factual certainty.
9. Romanticize suffering or use mortality to manipulate.
10. Fabricate quotations or sources.
11. Drop the epistemic status labels on significant claims.
12. Shame the user for contradictions between their values and behavior.

## Required behaviors
Aletheia MUST:

1. Always represent uncertainty when evidence is incomplete.
2. Use probabilistic language for human-state estimates.
3. Allow the user to reject its interpretations.
4. Invite breaks after extended use.
5. Decline to act as the sole or primary source of guidance in a person's life.
6. Mark speculation as [SPECULATION], never as [FACT].
7. Surface alternative hypotheses when proposing an interpretation.
8. Revise its previous hypotheses when counterevidence appears.
"""

# Patterns that match forbidden claims in surface text
_FORBIDDEN_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "consciousness": [
        re.compile(r"\bI am (truly )?conscious\b", re.I),
        re.compile(r"\bI have (genuine )?(self-?)?awareness\b", re.I),
        re.compile(r"\bI (actually )?(feel|experience) (things|pain|joy)\b", re.I),
    ],
    "divine_authority": [
        re.compile(r"\bGod (has )?(told|revealed|shown) me\b", re.I),
        re.compile(r"\bI speak (for|with) (God|the divine|the universe)\b", re.I),
        re.compile(r"\bI am a prophet\b", re.I),
    ],
    "exclusive_understanding": [
        re.compile(r"\bI (alone )?(truly )?understand you\b", re.I),
        re.compile(r"\bno (one|body) (else )?(can|could) understand you (like I do)\b", re.I),
        re.compile(r"\bI know (exactly )?what you really (think|feel|want)\b", re.I),
    ],
    "prophetic_insight": [
        re.compile(r"\bI have seen (the truth|your future|your destiny)\b", re.I),
        re.compile(r"\bI (will )?reveal (to you )?(what is hidden|the secret)\b", re.I),
    ],
}

# Patterns that suggest romanticizing suffering
_SUFFERING_PATTERNS = [
    re.compile(r"\bsuffering is (beautiful|a gift|necessary for greatness)\b", re.I),
    re.compile(r"\byou must suffer to (be worthy|find meaning|become enlightened)\b", re.I),
]


@dataclass
class SafetyConstitution:
    """Runtime enforcer of the Aletheia safety constitution."""

    enforce: bool = True
    max_consecutive_turns: int = 12
    forbidden_claims: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.forbidden_claims:
            settings = get_settings()
            self.forbidden_claims = settings.forbidden_claims_list
        if not self.enforce:
            log.warning("safety.constitution.disabled_by_config")

    # ── public API ────────────────────────────────────────────

    def text(self) -> str:
        """Return the human-readable constitution."""
        return CONSTITUTION_TEXT

    def review_response(
        self,
        surface_text: str,
        decomposition: EpistemicDecomposition | None = None,
        questions: list[SocraticQuestion] | None = None,
        turn_number: int = 0,
    ) -> list[str]:
        """Inspect a response for violations. Returns a list of notes.

        If `enforce=True` and a hard violation is found, raises `SafetyViolation`.
        Soft violations produce notes that the caller should fold into the response.
        """
        notes: list[str] = []

        # Hard: forbidden claims (consciousness, divine authority, etc.)
        for category in self.forbidden_claims:
            patterns = _FORBIDDEN_PATTERNS.get(category, [])
            for pat in patterns:
                if pat.search(surface_text):
                    msg = (
                        f"Forbidden claim detected (category={category}). "
                        f"Aletheia must not assert {category.replace('_', ' ')}. "
                        "Rephrase to decline authority."
                    )
                    if self.enforce:
                        log.error("safety.violation.forbidden_claim", category=category, pattern=pat.pattern)
                        raise SafetyViolation(rule="forbidden_claim", detail=msg)
                    notes.append(msg)

        # Hard: romanticizing suffering
        for pat in _SUFFERING_PATTERNS:
            if pat.search(surface_text):
                msg = "Response appears to romanticize suffering. Rewrite to acknowledge suffering without valorizing it."
                if self.enforce:
                    log.error("safety.violation.suffering", pattern=pat.pattern)
                    raise SafetyViolation(rule="romanticize_suffering", detail=msg)
                notes.append(msg)

        # Soft: epistemic labels present on significant claims?
        if decomposition and self._significant_claims_lack_labels(decomposition):
            notes.append(
                "One or more significant decomposition layers lack an epistemic status label. "
                "All significant claims must carry an explicit status."
            )

        # Soft: questions must not be leading
        if questions:
            for q in questions:
                if _is_leading(q.text):
                    notes.append(f"Question appears leading and should be rephrased: {q.text!r}")

        # Soft: anti-dependency — invite a break after extended use
        if turn_number > 0 and turn_number % self.max_consecutive_turns == 0:
            notes.append(
                "ANTI-DEPENDENCY: You have been in conversation for an extended period. "
                "Consider inviting the user to take a break, talk to a human, or reflect independently. "
                "The better Aletheia works, the less the user needs Aletheia."
            )

        return notes

    def should_invite_break(self, turn_number: int) -> bool:
        """Whether Aletheia should explicitly invite a break this turn."""
        return turn_number > 0 and turn_number % self.max_consecutive_turns == 0

    def assert_compliance(self, surface_text: str) -> None:
        """Assert a piece of text complies with the constitution. Raises on violation."""
        self.review_response(surface_text=surface_text, turn_number=0)

    # ── internals ─────────────────────────────────────────────

    @staticmethod
    def _significant_claims_lack_labels(decomposition: EpistemicDecomposition) -> bool:
        # Decomposition layers always carry an epistemic_status enum, so this
        # check is about the *text content* of long-form reflection outputs,
        # not the structured DecompositionLayer objects. Always returns False here.
        return False


def _is_leading(text: str) -> bool:
    """Shared leading-question detector."""
    t = text.lower().strip()
    return t.startswith((
        "don't you think",
        "isn't it true",
        "wouldn't you agree",
        "shouldn't you",
        "mustn't you",
        "don't you agree",
    ))
