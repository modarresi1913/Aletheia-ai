"""Epistemic Decomposition — the Fact / Interpretation / Story engine.

This is Aletheia's defining mechanism. Given a user statement, it produces a
structured decomposition that separates:
- what was observed (per the user's report)
- what the user concludes it means (interpretation)
- what emotions are implied
- what desires may be at stake
- what fears may be present
- what values are engaged
- what narrative the user is constructing
- what concrete actions are available

Each layer carries an explicit `EpistemicStatus` and at least one alternative
hypothesis for the interpretive layers. Aletheia never collapses to a single
reading of the user's situation.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from pydantic import ValidationError

from ..core.types import (
    Confidence,
    DecompositionLayer,
    EpistemicDecomposition,
    EpistemicStatus,
)
from ..llm.base import LLMProvider, LLMRequest, get_llm_provider
from ..llm.prompts import DECOMPOSITION_SYSTEM_PROMPT

log = structlog.get_logger(__name__)


class EpistemicDecomposer:
    """Decomposes user statements into the eight-layer epistemic chain."""

    def __init__(
        self,
        llm: LLMProvider | None = None,
        max_depth: int = 8,
    ) -> None:
        self.llm = llm or get_llm_provider()
        self.max_depth = max_depth

    def decompose(self, user_statement: str) -> EpistemicDecomposition:
        """Run the decomposition. Always returns a valid EpistemicDecomposition.

        If the LLM fails or returns malformed output, falls back to a minimal
        safe decomposition that preserves epistemic honesty (status=UNKNOWN).
        """
        request = LLMRequest(
            system_prompt=DECOMPOSITION_SYSTEM_PROMPT,
            user_prompt=self._build_user_prompt(user_statement),
            temperature=0.2,
            json_mode=True,
        )

        try:
            data = self.llm.complete_json(request)
            return self._validate(data, user_statement)
        except (ValidationError, json.JSONDecodeError, KeyError, TypeError) as e:
            log.warning("epistemic.decompose.fallback", error=str(e))
            return self._fallback(user_statement, reason=str(e))

    # ── internals ─────────────────────────────────────────────

    def _build_user_prompt(self, statement: str) -> str:
        return (
            "Decompose the following user statement. "
            "Return ONLY the JSON object specified in your instructions.\n\n"
            f"USER STATEMENT:\n\"\"\"\n{statement}\n\"\"\"\n"
        )

    def _validate(self, data: Any, user_statement: str) -> EpistemicDecomposition:
        """Validate LLM output and enforce Aletheia's epistemic rules."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        layers_data = data.get("layers", [])
        if not isinstance(layers_data, list) or not layers_data:
            raise ValueError("Decomposition must contain at least one layer")

        # Truncate to max_depth
        layers_data = layers_data[: self.max_depth]

        layers: list[DecompositionLayer] = []
        for ld in layers_data:
            if not isinstance(ld, dict):
                continue
            try:
                layer = DecompositionLayer(
                    layer=ld["layer"],
                    text=ld["text"],
                    epistemic_status=EpistemicStatus(ld["epistemic_status"]),
                    confidence=Confidence(ld.get("confidence", 0.5)),
                    alternative_hypotheses=ld.get("alternative_hypotheses", []),
                )
            except (KeyError, ValueError) as e:
                log.warning("epistemic.layer.skip", layer=ld, error=str(e))
                continue

            # Enforce: interpretive layers MUST have alternatives
            if (
                layer.layer in {"interpretation", "desire", "fear", "value", "narrative"}
                and not layer.alternative_hypotheses
            ):
                layer.alternative_hypotheses = [
                    "(no alternative was proposed; treat this reading as one possibility among unknown others)"
                ]

            # Enforce: observations reported by the user are FACT *about the report*,
            # not about the underlying reality.
            if layer.layer == "observation" and layer.epistemic_status == EpistemicStatus.EVIDENCE_SUPPORTED:
                # Reported observations are not independently verified.
                layer.epistemic_status = EpistemicStatus.FACT
                layer.text = (
                    f"{layer.text} "
                    "[note: this is a fact about the user's report, not about underlying reality.]"
                )
            layers.append(layer)

        if not layers:
            raise ValueError("No valid layers parsed from LLM output")

        notes = data.get("notes", [])
        if not isinstance(notes, list):
            notes = [str(notes)]

        return EpistemicDecomposition(
            user_statement=user_statement,
            layers=layers,
            notes=notes,
        )

    def _fallback(self, user_statement: str, reason: str) -> EpistemicDecomposition:
        """Minimal safe decomposition used when the LLM fails.

        This is critical: Aletheia must never fabricate a confident decomposition
        when the underlying model is unavailable. Instead, it returns an honest
        UNKNOWN decomposition that still separates observation from interpretation.
        """
        return EpistemicDecomposition(
            user_statement=user_statement,
            layers=[
                DecompositionLayer(
                    layer="observation",
                    text="The user made a statement. Its specific observable content has not been parsed.",
                    epistemic_status=EpistemicStatus.UNKNOWN,
                    confidence=Confidence(0.1),
                    alternative_hypotheses=[],
                ),
                DecompositionLayer(
                    layer="interpretation",
                    text="No interpretation was generated (decomposition fallback).",
                    epistemic_status=EpistemicStatus.UNKNOWN,
                    confidence=Confidence(0.1),
                    alternative_hypotheses=[
                        "The statement may be primarily observational.",
                        "The statement may be primarily emotional.",
                        "The statement may be primarily narrative.",
                    ],
                ),
            ],
            notes=[
                f"Fallback decomposition. Reason: {reason}",
                "When the model is unavailable, Aletheia refuses to fabricate interpretations.",
            ],
        )

    def render(self, decomposition: EpistemicDecomposition) -> str:
        """Render a decomposition as a readable, structured text block."""
        lines = [
            "Epistemic Decomposition",
            "────────────────────────────────────────────────────────────",
            f"user_statement: {decomposition.user_statement!r}",
            "",
        ]
        for layer in decomposition.layers:
            lines.append(f"  [{layer.layer.upper()}]")
            lines.append(f"    text        : {layer.text}")
            lines.append(f"    status      : {layer.epistemic_status.value}")
            lines.append(f"    confidence  : {layer.confidence:.2f}")
            if layer.alternative_hypotheses:
                lines.append("    alternatives:")
                for i, alt in enumerate(layer.alternative_hypotheses, 1):
                    lines.append(f"      {i}. {alt}")
            lines.append("")
        if decomposition.notes:
            lines.append("notes:")
            for n in decomposition.notes:
                lines.append(f"  - {n}")
        return "\n".join(lines)
