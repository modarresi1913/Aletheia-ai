"""Deterministic mock LLM provider for tests and offline development.

Produces structured responses that exercise Aletheia's parsers without requiring
an external model. Useful for CI, demos on machines without Ollama, and unit tests.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from .base import LLMProvider, LLMRequest, LLMResponse


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


class MockProvider(LLMProvider):
    """Returns canned but plausible structured responses.

    The mock inspects the system prompt to decide what shape to return. This
    keeps tests deterministic while still exercising the parsing code paths.
    """

    name = "mock"

    def complete(self, request: LLMRequest) -> LLMResponse:
        sp = request.system_prompt
        up = request.user_prompt

        if "Epistemic Decomposition" in sp:
            text = self._decomposition(up)
        elif "Socratic Engine" in sp:
            text = self._socratic(up)
        elif "Human State" in sp:
            text = self._human_state(up)
        elif "Five-Layer Reflection" in sp:
            text = self._reflection(up)
        else:
            text = (
                "[INTERPRETATION] This is a mock response from Aletheia's MockProvider. "
                "Configure a real provider (ollama, openai, anthropic) to use Aletheia fully."
            )

        return LLMResponse(
            text=text,
            model="mock-0.1",
            usage={"prompt_tokens": len(up) // 4, "completion_tokens": len(text) // 4},
        )

    # ── canned structured outputs ─────────────────────────────

    @staticmethod
    def _decomposition(user_statement: str) -> str:
        data: dict[str, Any] = {
            "user_statement": user_statement,
            "layers": [
                {
                    "layer": "observation",
                    "text": "The user reports a situation involving other people and an interpretation of their intent.",
                    "epistemic_status": "FACT",
                    "confidence": 0.7,
                    "alternative_hypotheses": [],
                },
                {
                    "layer": "interpretation",
                    "text": "The user interprets others' behavior as hostile or unsupportive.",
                    "epistemic_status": "INTERPRETATION",
                    "confidence": 0.4,
                    "alternative_hypotheses": [
                        "The behavior may be unrelated to the user.",
                        "The user may be projecting a prior conflict onto neutral events.",
                        "The situation may reflect organizational stress rather than personal hostility.",
                    ],
                },
                {
                    "layer": "emotion",
                    "text": "Likely fear, frustration, or humiliation.",
                    "epistemic_status": "PLAUSIBLE",
                    "confidence": 0.5,
                    "alternative_hypotheses": ["calm detachment", "anticipation"],
                },
                {
                    "layer": "desire",
                    "text": "Autonomy, recognition, or safety.",
                    "epistemic_status": "SPECULATION",
                    "confidence": 0.35,
                    "alternative_hypotheses": ["belonging", "novelty"],
                },
                {
                    "layer": "fear",
                    "text": "Fear of failure, judgment, or loss of standing.",
                    "epistemic_status": "SPECULATION",
                    "confidence": 0.35,
                    "alternative_hypotheses": ["fear of disappointing others", "fear of regret"],
                },
                {
                    "layer": "value",
                    "text": "Dignity or independence may be at stake.",
                    "epistemic_status": "PHILOSOPHICAL-VIEW",
                    "confidence": 0.3,
                    "alternative_hypotheses": ["stability", "loyalty"],
                },
                {
                    "layer": "narrative",
                    "text": "The user is constructing a story in which they must leave to preserve themselves.",
                    "epistemic_status": "INTERPRETATION",
                    "confidence": 0.4,
                    "alternative_hypotheses": [
                        "a story in which they must prove themselves by staying",
                    ],
                },
                {
                    "layer": "possible_action",
                    "text": "A short observation period before any irreversible decision.",
                    "epistemic_status": "PLAUSIBLE",
                    "confidence": 0.6,
                    "alternative_hypotheses": [
                        "a direct conversation with the people involved",
                        "consulting someone outside the situation",
                    ],
                },
            ],
            "notes": [
                "Mock decomposition. Replace with a real provider for genuine analysis.",
                "All interpretations are tentative; multiple alternatives are listed by design.",
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def _socratic(user_statement: str) -> str:
        data = {
            "questions": [
                {
                    "text": "Which part of what you described is something you directly observed, and which part is your interpretation of why it happened?",
                    "purpose": "Separate observation from interpretation before deciding.",
                    "targeted_layer": "epistemic",
                    "epistemic_status": "INTERPRETATION",
                    "is_open": True,
                },
                {
                    "text": "If you knew with certainty that nobody would judge your decision, what would you choose?",
                    "purpose": "Test whether the obstacle is the choice or the perceived audience.",
                    "targeted_layer": "psychological",
                    "epistemic_status": "INTERPRETATION",
                    "is_open": True,
                },
                {
                    "text": "What evidence, if it appeared in the next week, would change your mind about leaving?",
                    "purpose": "Identify whether the conclusion is fixed or evidence-sensitive.",
                    "targeted_layer": "epistemic",
                    "epistemic_status": "INTERPRETATION",
                    "is_open": True,
                },
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def _human_state(user_statement: str) -> str:
        data = {
            "primary_signals": ["fear", "internal_conflict"],
            "confidence": 0.45,
            "evidence_snippets": [user_statement[:140]],
            "alternative_signals": ["anger", "uncertainty"],
            "notes": [
                "Mock estimate. Confidence is intentionally below 0.5 to model uncertainty.",
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def _reflection(user_statement: str) -> str:
        data = {
            "layers": {
                "epistemic": (
                    "[FACT] The user reports a situation. [INTERPRETATION] Their conclusion "
                    "about others' intent is not directly observable. [SPECULATION] An alternative "
                    "reading is that the situation reflects organizational conditions rather than personal hostility."
                ),
                "psychological": (
                    "[PLAUSIBLE] Fear and a need for autonomy appear present. [SPECULATION] The "
                    "user may also be protecting an identity-based narrative about being unsupported."
                ),
                "practical": (
                    "[PLAUSIBLE] The user is considering a major decision. [PLAUSIBLE] Reversible "
                    "intermediate steps (observation, conversation) likely exist before any irreversible action."
                ),
                "ethical": (
                    "[INTERPRETATION] Others may be affected by the user's decision. [SPECULATION] "
                    "Their perspectives are not represented in the current statement."
                ),
                "existential": (
                    "[PHILOSOPHICAL-VIEW] Existentialist traditions treat such moments as sites where "
                    "freedom and anxiety appear together (Kierkegaard, Sartre). [SPECULATION] The "
                    "decision may matter less for its outcome than for what the user learns about their own values."
                ),
            },
            "possible_actions": [
                "Seven-day observation period with daily notes on what actually happens vs. what is interpreted.",
                "One direct conversation with the person most involved, asking only clarifying questions.",
                "Write two parallel future narratives (stay / leave) and revisit in one week.",
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
