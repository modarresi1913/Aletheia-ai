"""Socratic Engine.

Generates context-sensitive questions that help the user examine their own
assumptions. Questions are never leading; they never imply the user is wrong
or steer toward a predetermined conclusion.

Question categories (used as fallback / heuristic seeding):

- observation vs interpretation
- audience test ("if nobody knew...")
- fear-removal test
- goal vs identity
- belief-protection test
- evidence-sensitivity test
- counterfactual stability
- cost of being wrong
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from pydantic import ValidationError

from ..core.types import (
    EpistemicDecomposition,
    EpistemicStatus,
    HumanStateEstimate,
    ReflectionLayer,
    SocraticQuestion,
)
from ..llm.base import LLMProvider, LLMRequest, get_llm_provider
from ..llm.prompts import SOCRATIC_SYSTEM_PROMPT

log = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────
# Heuristic fallback question bank
# ─────────────────────────────────────────────────────────────
# These are used when the LLM is unavailable or returns malformed output.
# Each entry is (text, purpose, targeted_layer).

_FALLBACK_QUESTIONS: list[tuple[str, str, ReflectionLayer]] = [
    (
        "Which part of what you described is something you directly observed, and which part is your interpretation of why it happened?",
        "Separate observation from interpretation.",
        ReflectionLayer.EPISTEMIC,
    ),
    (
        "If nobody whose opinion matters to you would ever know about this decision, what would you choose?",
        "Test whether the obstacle is the choice or the perceived audience.",
        ReflectionLayer.PSYCHOLOGICAL,
    ),
    (
        "What would you still want if fear were removed from the equation?",
        "Distinguish genuine preference from fear-driven avoidance.",
        ReflectionLayer.PSYCHOLOGICAL,
    ),
    (
        "Are you pursuing this goal, or the identity you believe comes with it?",
        "Separate goal from identity attachment.",
        ReflectionLayer.EXISTENTIAL,
    ),
    (
        "What evidence, if it appeared in the next week, would change your mind?",
        "Test whether the conclusion is evidence-sensitive or fixed.",
        ReflectionLayer.EPISTEMIC,
    ),
    (
        "What are you protecting by maintaining this belief?",
        "Surface the protective function of a held belief.",
        ReflectionLayer.PSYCHOLOGICAL,
    ),
    (
        "Who else is affected by this situation, and how might they describe it differently?",
        "Expand the ethical frame beyond the user's perspective.",
        ReflectionLayer.ETHICAL,
    ),
    (
        "If you took the opposite action and it turned out badly, what specifically would be lost?",
        "Make the cost of error concrete.",
        ReflectionLayer.PRACTICAL,
    ),
    (
        "Five years from now, which decision would still feel like yours?",
        "Test for long-term alignment with self.",
        ReflectionLayer.EXISTENTIAL,
    ),
    (
        "What is the smallest reversible step you could take before committing to anything irreversible?",
        "Convert reflection into a low-cost experiment.",
        ReflectionLayer.PRACTICAL,
    ),
]


class SocraticEngine:
    """Generates high-quality questions for a user statement."""

    def __init__(
        self,
        llm: LLMProvider | None = None,
        max_questions: int = 3,
    ) -> None:
        self.llm = llm or get_llm_provider()
        self.max_questions = max_questions

    def generate(
        self,
        user_statement: str,
        decomposition: EpistemicDecomposition | None = None,
        human_state: HumanStateEstimate | None = None,
        max_questions: int | None = None,
    ) -> list[SocraticQuestion]:
        """Generate up to `max_questions` context-sensitive questions."""
        n = max_questions or self.max_questions

        request = LLMRequest(
            system_prompt=SOCRATIC_SYSTEM_PROMPT,
            user_prompt=self._build_prompt(user_statement, decomposition, human_state, n),
            temperature=0.5,
            json_mode=True,
        )

        try:
            data = self.llm.complete_json(request)
            return self._validate(data, n)
        except (ValidationError, json.JSONDecodeError, KeyError, TypeError) as e:
            log.warning("socratic.fallback", error=str(e))
            return self._fallback(n)

    # ── internals ─────────────────────────────────────────────

    def _build_prompt(
        self,
        statement: str,
        decomposition: EpistemicDecomposition | None,
        human_state: HumanStateEstimate | None,
        n: int,
    ) -> str:
        parts = [
            f"USER STATEMENT:\n\"\"\"\n{statement}\n\"\"\"",
            f"\nGenerate up to {n} high-quality Socratic questions.",
        ]
        if decomposition is not None:
            interp_layers = [layer for layer in decomposition.layers if layer.layer == "interpretation"]
            if interp_layers:
                parts.append(
                    "\nDetected interpretation(s) to probe:\n"
                    + "\n".join(f"- {layer.text}" for layer in interp_layers)
                )
        if human_state is not None and human_state.primary_signals:
            parts.append(
                "\nEstimated user signals (weak evidence, not a diagnosis):\n"
                + ", ".join(s.value for s in human_state.primary_signals)
            )
        parts.append("\nReturn ONLY the JSON object specified in your instructions.")
        return "\n".join(parts)

    def _validate(self, data: Any, n: int) -> list[SocraticQuestion]:
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")
        raw_questions = data.get("questions", [])
        if not isinstance(raw_questions, list):
            raise ValueError("`questions` must be a list")

        out: list[SocraticQuestion] = []
        for qd in raw_questions[:n]:
            if not isinstance(qd, dict):
                continue
            try:
                layer_str = qd.get("targeted_layer")
                layer = ReflectionLayer(layer_str) if layer_str else None
                q = SocraticQuestion(
                    text=qd["text"],
                    purpose=qd.get("purpose", ""),
                    targeted_layer=layer,
                    epistemic_status=EpistemicStatus(
                        qd.get("epistemic_status", "INTERPRETATION")
                    ),
                    is_open=qd.get("is_open", True),
                )
            except (KeyError, ValueError) as e:
                log.warning("socratic.question.skip", q=qd, error=str(e))
                continue

            # Enforce: questions must not be leading ("Don't you think...?")
            if self._is_leading(q.text):
                log.info("socratic.question.leading_filtered", text=q.text)
                continue

            out.append(q)
        return out

    def _fallback(self, n: int) -> list[SocraticQuestion]:
        """Use the static question bank when the LLM is unavailable."""
        out: list[SocraticQuestion] = []
        for text, purpose, layer in _FALLBACK_QUESTIONS[:n]:
            out.append(
                SocraticQuestion(
                    text=text,
                    purpose=purpose,
                    targeted_layer=layer,
                    epistemic_status=EpistemicStatus.INTERPRETATION,
                    is_open=True,
                )
            )
        return out

    @staticmethod
    def _is_leading(text: str) -> bool:
        """Crude detector for leading questions.

        A leading question implies the answer in its wording. This heuristic
        catches common patterns; it is intentionally conservative.
        """
        t = text.lower().strip()
        leading_starts = (
            "don't you think",
            "isn't it true",
            "wouldn't you agree",
            "shouldn't you",
            "mustn't you",
            "don't you agree",
        )
        return any(t.startswith(p) for p in leading_starts)
