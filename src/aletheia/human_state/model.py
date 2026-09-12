"""Non-diagnostic Human State Model.

Estimates likely conversational signals (uncertainty, fear, grief, anger, ...)
from the user's statement. These are NOT medical or psychological diagnoses.
The model always represents uncertainty.

Output language rules:
- Use probabilistic phrasing ("One possibility is...", "weak evidence for...")
- Confidence must remain below 0.95 by design (enforced in the type system)
- Always include alternative signals when primary signals are non-empty
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from pydantic import ValidationError

from ..core.types import Confidence, HumanStateEstimate, HumanStateSignal
from ..llm.base import LLMProvider, LLMRequest, get_llm_provider
from ..llm.prompts import HUMAN_STATE_SYSTEM_PROMPT

log = structlog.get_logger(__name__)


# Heuristic signal lexicon — used when the LLM is unavailable.
# Each signal maps to a list of (lowercased) cue phrases.
_LEXICON: dict[HumanStateSignal, list[str]] = {
    HumanStateSignal.FEAR: ["afraid", "scared", "worried", "anxious", "fear", "terrified", "dread"],
    HumanStateSignal.ANGER: ["angry", "furious", "rage", "resent", "frustrated", "bitter"],
    HumanStateSignal.GRIEF: ["lost", "grief", "mourn", "miss them", "death", "died", "gone"],
    HumanStateSignal.UNCERTAINTY: ["confused", "don't know", "unsure", "uncertain", "torn", "can't decide"],
    HumanStateSignal.SHAME: ["ashamed", "embarrassed", "humiliated", "stupid", "failure"],
    HumanStateSignal.COMPARISON: ["better than", "worse than", "everyone else", "they have", "i wish i"],
    HumanStateSignal.ATTACHMENT: ["can't let go", "need them", "must have", "attached", "cling"],
    HumanStateSignal.NEED_FOR_APPROVAL: ["what will they think", "approval", "validate", "prove myself"],
    HumanStateSignal.DESIRE_FOR_CONTROL: ["must", "have to", "in control", "should be able to", "manage everything"],
    HumanStateSignal.EXISTENTIAL_CONFUSION: ["what's the point", "meaning", "why am i", "purpose", "empty"],
    HumanStateSignal.AVOIDANCE: ["don't want to think", "rather not", "change the subject", "later"],
    HumanStateSignal.INTERNAL_CONFLICT: ["but also", "on the other hand", "part of me", "torn between"],
    HumanStateSignal.CALM: ["calm", "settled", "clear", "grounded", "at peace"],
    HumanStateSignal.CURIOSITY: ["curious", "wonder", "interested", "explore", "learn"],
}


class HumanStateModel:
    """Estimates likely user signals without ever producing a diagnosis."""

    def __init__(self, llm: LLMProvider | None = None) -> None:
        self.llm = llm or get_llm_provider()

    def estimate(
        self,
        user_statement: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> HumanStateEstimate:
        """Produce a non-diagnostic HumanStateEstimate."""
        request = LLMRequest(
            system_prompt=HUMAN_STATE_SYSTEM_PROMPT,
            user_prompt=self._build_prompt(user_statement, conversation_history or []),
            temperature=0.2,
            json_mode=True,
        )
        try:
            data = self.llm.complete_json(request)
            return self._validate(data, user_statement)
        except (ValidationError, json.JSONDecodeError, KeyError, TypeError) as e:
            log.warning("human_state.fallback", error=str(e))
            return self._heuristic(user_statement)

    # ── internals ─────────────────────────────────────────────

    def _build_prompt(self, statement: str, history: list[dict[str, str]]) -> str:
        parts = [f"USER STATEMENT:\n\"\"\"\n{statement}\n\"\"\""]
        if history:
            last_turns = history[-3:]
            parts.append("\nRECENT HISTORY:")
            for t in last_turns:
                parts.append(f"  [{t.get('role', '?')}] {t.get('content', '')[:200]}")
        parts.append("\nReturn ONLY the JSON object specified in your instructions.")
        return "\n".join(parts)

    def _validate(self, data: Any, user_statement: str) -> HumanStateEstimate:
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")
        primary_raw = data.get("primary_signals", [])
        alt_raw = data.get("alternative_signals", [])

        def _parse_signals(raw: Any) -> list[HumanStateSignal]:
            out: list[HumanStateSignal] = []
            if not isinstance(raw, list):
                return out
            for s in raw:
                try:
                    out.append(HumanStateSignal(s))
                except ValueError:
                    log.warning("human_state.unknown_signal", signal=s)
            return out

        primary = _parse_signals(primary_raw)
        alt = _parse_signals(alt_raw)

        # Enforce: when primary is non-empty, alternatives must be present
        if primary and not alt:
            alt = [HumanStateSignal.UNKNOWN] if hasattr(HumanStateSignal, "UNKNOWN") else []
            # Fallback: pick from lexicon
            if not alt:
                alt = [s for s in HumanStateSignal if s not in primary][:1]

        conf = float(data.get("confidence", 0.4))
        conf = max(0.0, min(0.94, conf))  # hard cap below 0.95

        evidence = data.get("evidence_snippets", [])
        if not isinstance(evidence, list):
            evidence = [str(evidence)]

        notes = data.get("notes", [])
        if not isinstance(notes, list):
            notes = [str(notes)]

        return HumanStateEstimate(
            primary_signals=primary,
            confidence=Confidence(conf),
            evidence_snippets=evidence,
            alternative_signals=alt,
        )

    def _heuristic(self, user_statement: str) -> HumanStateEstimate:
        """Lexicon-based fallback. Crude, but always returns a valid estimate."""
        text = user_statement.lower()
        scores: dict[HumanStateSignal, int] = {}
        for signal, cues in _LEXICON.items():
            n = sum(text.count(cue) for cue in cues)
            if n > 0:
                scores[signal] = n

        if not scores:
            return HumanStateEstimate(
                primary_signals=[HumanStateSignal.CURIOSITY],
                confidence=Confidence(0.2),
                evidence_snippets=[user_statement[:140]],
                alternative_signals=[HumanStateSignal.UNCERTAINTY],
            )

        sorted_signals = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = [s for s, _ in sorted_signals[:3]]
        alt = [s for s, _ in sorted_signals[3:5]] or [
            s for s in HumanStateSignal if s not in primary
        ][:1]
        # Confidence scaled to total matches, capped at 0.5 for the heuristic path
        total = sum(scores.values())
        conf = min(0.5, 0.15 + 0.05 * total)

        return HumanStateEstimate(
            primary_signals=primary,
            confidence=Confidence(conf),
            evidence_snippets=[user_statement[:140]],
            alternative_signals=alt,
        )
