"""Five-Layer Reflection Engine.

Every important user statement may pass through up to five reflection layers:

1. EPISTEMIC       — What do we actually know?
2. PSYCHOLOGICAL   — What emotions, assumptions, and cognitive patterns may be involved?
3. PRACTICAL       — What is happening in the real world? What actions are available?
4. ETHICAL         — Who else may be affected?
5. EXISTENTIAL     — What does this reveal about meaning, identity, mortality, freedom, or purpose?

The engine does NOT force all five layers into every response. It invokes only
the layers that are contextually appropriate (or explicitly requested).
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from pydantic import ValidationError

from ..core.config import get_settings
from ..core.types import (
    EpistemicDecomposition,
    HumanStateEstimate,
    ReflectionLayer,
    ReflectionResult,
    SocraticQuestion,
)
from ..epistemic.decomposition import EpistemicDecomposer
from ..human_state.model import HumanStateModel
from ..llm.base import LLMProvider, LLMRequest, get_llm_provider
from ..llm.prompts import REFLECTION_SYSTEM_PROMPT
from ..safety.constitution import SafetyConstitution
from ..socratic.engine import SocraticEngine
from ..wisdom.graph import WisdomGraph
from ..wisdom.retrieval import WisdomRetriever

log = structlog.get_logger(__name__)


class FiveLayerReflectionEngine:
    """Coordinates decomposition, reflection, socratic generation, and safety."""

    def __init__(
        self,
        llm: LLMProvider | None = None,
        decomposer: EpistemicDecomposer | None = None,
        socratic: SocraticEngine | None = None,
        human_state_model: HumanStateModel | None = None,
        wisdom_graph: WisdomGraph | None = None,
        wisdom_retriever: WisdomRetriever | None = None,
        safety: SafetyConstitution | None = None,
    ) -> None:
        self.llm = llm or get_llm_provider()
        self.decomposer = decomposer or EpistemicDecomposer(llm=self.llm)
        self.socratic = socratic or SocraticEngine(llm=self.llm)
        self.human_state = human_state_model or HumanStateModel(llm=self.llm)
        self.wisdom_graph = wisdom_graph or WisdomGraph.default()
        self.wisdom_retriever = wisdom_retriever or WisdomRetriever(self.wisdom_graph)
        self.safety = safety or SafetyConstitution()

    def reflect(
        self,
        user_statement: str,
        requested_layers: list[ReflectionLayer] | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        max_questions: int = 3,
    ) -> ReflectionResult:
        """Run the full reflection pipeline for a single user statement."""
        settings = get_settings()

        # Determine layers to invoke
        layers_to_invoke = self._select_layers(
            user_statement, requested_layers, settings
        )

        # 1. Epistemic decomposition
        decomposition = self.decomposer.decompose(user_statement)

        # 2. Human state estimate
        human_state = self.human_state.estimate(
            user_statement, conversation_history=conversation_history or []
        )

        # 3. Wisdom retrieval (semantic-ish keyword match for MVP)
        wisdom_claims = self.wisdom_retriever.retrieve(user_statement, top_k=3)

        # 4. Five-layer reflection (only requested layers)
        layer_outputs = self._reflect_layers(
            user_statement, decomposition, human_state, layers_to_invoke
        )

        # 5. Socratic questions
        questions = self.socratic.generate(
            user_statement,
            decomposition=decomposition,
            human_state=human_state,
            max_questions=max_questions,
        )

        # 6. Possible actions (extracted from reflection output)
        possible_actions = self._extract_possible_actions(layer_outputs)

        # 7. Safety check
        safety_notes = self.safety.review_response(
            surface_text=self._compose_surface(layer_outputs, questions),
            decomposition=decomposition,
            questions=questions,
            turn_number=len(conversation_history or []),
        )

        return ReflectionResult(
            decomposition=decomposition,
            layers_invoked=layers_to_invoke,
            layer_outputs=layer_outputs,
            socratic_questions=questions,
            wisdom_retrieved=wisdom_claims,
            human_state=human_state,
            possible_actions=possible_actions,
            safety_notes=safety_notes,
            meta={"provider": self.llm.name},
        )

    # ── internals ─────────────────────────────────────────────

    def _select_layers(
        self,
        statement: str,
        requested: list[ReflectionLayer] | None,
        settings: Any,
    ) -> list[ReflectionLayer]:
        if requested:
            return requested
        configured = [
            ReflectionLayer(s.strip())
            for s in settings.reflection_layer_list
            if s.strip()
        ]
        return configured or list(ReflectionLayer)

    def _reflect_layers(
        self,
        statement: str,
        decomposition: EpistemicDecomposition,
        human_state: HumanStateEstimate,
        layers: list[ReflectionLayer],
    ) -> dict[str, str]:
        if not layers:
            return {}

        request = LLMRequest(
            system_prompt=REFLECTION_SYSTEM_PROMPT,
            user_prompt=self._build_reflection_prompt(statement, decomposition, human_state, layers),
            temperature=0.4,
            json_mode=True,
        )

        try:
            data = self.llm.complete_json(request)
            raw_layers = data.get("layers", {}) if isinstance(data, dict) else {}
            if not isinstance(raw_layers, dict):
                raw_layers = {}
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as e:
            log.warning("reflection.fallback", error=str(e))
            raw_layers = self._fallback_layers(statement, layers)

        # Only keep layers we requested
        out: dict[str, str] = {}
        for layer in layers:
            text = raw_layers.get(layer.value)
            if not text:
                text = self._fallback_layer_text(layer, statement)
            # Ensure at least one epistemic label appears
            if not self._has_epistemic_label(text):
                text = f"[INTERPRETATION] {text}"
            out[layer.value] = text
        return out

    def _build_reflection_prompt(
        self,
        statement: str,
        decomposition: EpistemicDecomposition,
        human_state: HumanStateEstimate,
        layers: list[ReflectionLayer],
    ) -> str:
        layer_names = ", ".join(layer.value for layer in layers)
        decomp_summary = "\n".join(
            f"- {layer.layer}: {layer.text} [{layer.epistemic_status.value}]"
            for layer in decomposition.layers[:4]
        )
        signals = ", ".join(s.value for s in human_state.primary_signals) or "none"
        return (
            f"USER STATEMENT:\n\"\"\"\n{statement}\n\"\"\"\n\n"
            f"Reflect on these layers only: {layer_names}\n\n"
            f"Decomposition summary:\n{decomp_summary}\n\n"
            f"Estimated user signals (weak evidence): {signals}\n\n"
            "Return ONLY the JSON object specified in your instructions."
        )

    def _fallback_layers(
        self, statement: str, layers: list[ReflectionLayer]
    ) -> dict[str, str]:
        return {layer.value: self._fallback_layer_text(layer, statement) for layer in layers}

    @staticmethod
    def _fallback_layer_text(layer: ReflectionLayer, statement: str) -> str:
        s = statement[:200]
        if layer == ReflectionLayer.EPISTEMIC:
            return (
                f"[FACT] The user said: {s!r}. "
                "[INTERPRETATION] The user's framing of the situation is one possible reading. "
                "[SPECULATION] An alternative reading cannot be generated without a working model."
            )
        if layer == ReflectionLayer.PSYCHOLOGICAL:
            return (
                "[UNKNOWN] Psychological patterns cannot be estimated without a working model. "
                "[SPECULATION] Avoid assuming specific emotions or motivations from the text alone."
            )
        if layer == ReflectionLayer.PRACTICAL:
            return (
                "[PLAUSIBLE] The user is in a situation with available actions. "
                "[PLAUSIBLE] Reversible intermediate steps likely exist before any irreversible action."
            )
        if layer == ReflectionLayer.ETHICAL:
            return (
                "[INTERPRETATION] Other people may be affected by the user's choices. "
                "[SPECULATION] Their perspectives are not represented in the current statement."
            )
        if layer == ReflectionLayer.EXISTENTIAL:
            return (
                "[PHILOSOPHICAL-VIEW] Existential traditions treat such moments as sites where "
                "freedom and anxiety appear together (Kierkegaard, Sartre). "
                "[SPECULATION] The decision may matter less for its outcome than for what it reveals about values."
            )
        return "[UNKNOWN]"

    @staticmethod
    def _has_epistemic_label(text: str) -> bool:
        for label in (
            "[FACT]",
            "[EVIDENCE-SUPPORTED]",
            "[PLAUSIBLE]",
            "[INTERPRETATION]",
            "[PHILOSOPHICAL-VIEW]",
            "[SPECULATION]",
            "[UNKNOWN]",
        ):
            if label in text:
                return True
        return False

    def _extract_possible_actions(
        self, layer_outputs: dict[str, str]
    ) -> list[str]:
        """Heuristic: extract action-like sentences from the practical layer."""
        text = layer_outputs.get("practical", "")
        if not text:
            return []
        actions: list[str] = []
        for sentence in text.split("."):
            s = sentence.strip()
            if not s:
                continue
            low = s.lower()
            if any(
                kw in low
                for kw in ("could", "might try", "consider", "experiment", "test", "observe", "ask")
            ):
                # Strip leading epistemic label
                if "]" in s:
                    s = s.split("]", 1)[1].strip()
                actions.append(s)
        return actions[:5]

    def _compose_surface(
        self,
        layer_outputs: dict[str, str],
        questions: list[SocraticQuestion],
    ) -> str:
        parts: list[str] = []
        for layer_name, text in layer_outputs.items():
            parts.append(f"{layer_name.upper()}\n{text}\n")
        if questions:
            parts.append("QUESTIONS FOR YOU")
            for i, q in enumerate(questions, 1):
                parts.append(f"{i}. {q.text}")
        return "\n".join(parts)
