"""Contradiction detection heuristics.

Detects tensions between:
- declared values and recent decisions
- stated beliefs and observed actions
- goals and behavior patterns
- identity claims and behavior
- contradictions within a single statement

The heuristics are deliberately conservative: false negatives are acceptable,
false positives (shaming the user) are not.
"""
from __future__ import annotations

import re

import structlog

from ..core.types import EpistemicStatus
from ..memory.entry import MemoryEntry
from ..memory.store import LongitudinalMemory
from .types import Contradiction, ContradictionDetection

log = structlog.get_logger(__name__)


# Lexicons for value categories and their opposing behavioral cues.
_VALUE_LEXICON: dict[str, list[str]] = {
    "freedom": ["freedom", "autonomy", "independence", "free", "liberty", "self-determination"],
    "security": ["security", "safety", "stable", "stability", "certain", "certainty", "predictable"],
    "adventure": ["adventure", "risk", "novelty", "exploration", "unknown", "bold"],
    "achievement": ["achievement", "success", "accomplish", "ambition", "excel", "drive"],
    "connection": ["connection", "relationship", "love", "belonging", "community", "intimacy"],
    "authenticity": ["authenticity", "true to myself", "genuine", "real", "honest"],
    "growth": ["growth", "learning", "development", "become", "evolve"],
    "peace": ["peace", "calm", "stillness", "quiet", "serenity"],
    "service": ["service", "contribute", "help", "give", "others"],
}

# Mapping: a declared value of category X suggests possible tension when
# recent decisions contain cues from category Y.
_OPPOSING_PAIRS: list[tuple[str, str]] = [
    ("freedom", "security"),
    ("adventure", "security"),
    ("authenticity", "achievement"),  # authenticity vs. status-seeking
    ("peace", "achievement"),
    ("connection", "autonomy"),
    ("service", "achievement"),
]


def _categorize_value(text: str) -> str | None:
    t = text.lower()
    for category, cues in _VALUE_LEXICON.items():
        if any(cue in t for cue in cues):
            return category
    return None


def _categorize_behavior(text: str) -> set[str]:
    t = text.lower()
    out: set[str] = set()
    for category, cues in _VALUE_LEXICON.items():
        if any(cue in t for cue in cues):
            out.add(category)
    return out


def _are_opposing(a: str, b: str) -> bool:
    return (a, b) in _OPPOSING_PAIRS or (b, a) in _OPPOSING_PAIRS


# ─────────────────────────────────────────────────────────────
# Intra-statement contradiction cues
# ─────────────────────────────────────────────────────────────

_INTRA_CONTRADICTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\bI want to\b[^.]*\bbut I (?:also|really) want to\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bI (?:need to|have to|must)\b[^.]*\bbut I (?:can't|cannot|don't want to)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bpart of me\b[^.]*\b(?:another part|the other part)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bon one hand\b[^.]*\bon the other hand\b",
        re.IGNORECASE,
    ),
]


class ContradictionDetector:
    """Detects contradictions between memory entries and within statements."""

    def __init__(self, memory: LongitudinalMemory | None = None) -> None:
        self.memory = memory or LongitudinalMemory()

    def detect_value_vs_decisions(
        self,
        user_id: str = "anonymous",
    ) -> list[Contradiction]:
        """Detect tensions between declared values and recent decisions."""
        contradictions: list[Contradiction] = []
        values = self.memory.declared_values(user_id)
        decisions = self.memory.decisions(user_id)

        if not values or not decisions:
            return contradictions

        for value in values:
            if not value.is_active():
                continue
            value_category = _categorize_value(value.text)
            if not value_category:
                continue
            for decision in decisions:
                if not decision.is_active():
                    continue
                decision_categories = _categorize_behavior(decision.text)
                for dec_cat in decision_categories:
                    if _are_opposing(value_category, dec_cat):
                        contradictions.append(
                            self._build_value_decision_contradiction(
                                value=value,
                                decision=decision,
                                value_category=value_category,
                                decision_category=dec_cat,
                            )
                        )
        return contradictions

    def detect_intra_statement(
        self,
        statement: str,
        user_id: str = "anonymous",
    ) -> list[Contradiction]:
        """Detect contradictions within a single user statement."""
        out: list[Contradiction] = []
        for pattern in _INTRA_CONTRADICTION_PATTERNS:
            match = pattern.search(statement)
            if match:
                out.append(
                    Contradiction(
                        id=f"contra_intra_{hash(match.group(0)) & 0xFFFFFFFF:08x}",
                        user_id=user_id,
                        kind="intra_statement",
                        description=(
                            "The statement contains an explicit internal tension "
                            f"(matched: {match.group(0)!r})."
                        ),
                        side_a="One part of the statement",
                        side_b="Another part of the statement",
                        side_a_kind="statement_segment",
                        side_b_kind="statement_segment",
                        evidence_a=[statement],
                        evidence_b=[],
                        interpretations=[
                            "There may be a genuine conflict between two real desires.",
                            "One desire may be aspirational and the other actual.",
                            "The conflict may reflect fear rather than genuine preference.",
                            "The two may not actually be in tension once examined carefully.",
                        ],
                    )
                )
        return out

    def detect_all(
        self,
        user_id: str = "anonymous",
        current_statement: str | None = None,
    ) -> ContradictionDetection:
        """Run all detectors and return a combined result."""
        contradictions: list[Contradiction] = []
        contradictions.extend(self.detect_value_vs_decisions(user_id))
        if current_statement:
            contradictions.extend(self.detect_intra_statement(current_statement, user_id))

        notes: list[str] = []
        if not contradictions:
            notes.append(
                "No active contradictions detected. Note: absence of detected contradiction "
                "does not imply absence of tension; the heuristics are conservative."
            )
        else:
            notes.append(
                "These contradictions are interpretations, not judgments. "
                "Each is offered with multiple possible readings."
            )

        return ContradictionDetection(
            contradictions=contradictions,
            notes=notes,
            epistemic_status=EpistemicStatus.INTERPRETATION,
        )

    # ── internals ─────────────────────────────────────────────

    @staticmethod
    def _build_value_decision_contradiction(
        value: MemoryEntry,
        decision: MemoryEntry,
        value_category: str,
        decision_category: str,
    ) -> Contradiction:
        return Contradiction(
            id=f"contra_vd_{value.id[:8]}_{decision.id[:8]}",
            user_id=value.user_id,
            kind="value_vs_decision",
            description=(
                f"Declared value '{value.text[:80]}' ({value_category}) "
                f"may be in tension with decision '{decision.text[:80]}' ({decision_category})."
            ),
            side_a=value.text,
            side_b=decision.text,
            side_a_kind="declared_value",
            side_b_kind="decision",
            side_a_entry_id=value.id,
            side_b_entry_id=decision.id,
            evidence_a=value.evidence,
            evidence_b=decision.evidence,
            interpretations=[
                (
                    f"The definition of '{value_category}' may have shifted; "
                    "the apparent contradiction may reflect a refined understanding "
                    "rather than inconsistency."
                ),
                (
                    f"'{value_category}' and '{decision_category}' may be in genuine tension. "
                    "Most humans hold values that conflict under some conditions."
                ),
                (
                    "The decision may be fear-driven rather than preference-driven. "
                    "Fear can produce behavior that diverges from declared values without "
                    "the values being false."
                ),
                (
                    "The declared value may be aspirational rather than actual. "
                    "This is not a moral failing; it is information."
                ),
            ],
        )


__all__ = ["ContradictionDetector"]
