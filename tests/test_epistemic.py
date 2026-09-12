"""Tests for the Epistemic Decomposition engine."""
from __future__ import annotations

from aletheia.core.types import EpistemicDecomposition, EpistemicStatus
from aletheia.epistemic.decomposition import EpistemicDecomposer
from aletheia.epistemic.labels import can_promote_to, label_strength, status_rank
from aletheia.llm.mock import MockProvider


class TestEpistemicLabels:
    def test_fact_is_strongest(self) -> None:
        assert status_rank(EpistemicStatus.FACT) == 7
        assert status_rank(EpistemicStatus.UNKNOWN) == 1

    def test_strong_moderate_weak(self) -> None:
        assert label_strength(EpistemicStatus.FACT) == "strong"
        assert label_strength(EpistemicStatus.PLAUSIBLE) == "moderate"
        assert label_strength(EpistemicStatus.SPECULATION) == "weak"

    def test_promotion_only_to_stronger(self) -> None:
        assert can_promote_to(EpistemicStatus.SPECULATION, EpistemicStatus.PLAUSIBLE)
        assert not can_promote_to(EpistemicStatus.PLAUSIBLE, EpistemicStatus.SPECULATION)


class TestEpistemicDecomposer:
    def setup_method(self) -> None:
        self.decomposer = EpistemicDecomposer(llm=MockProvider())

    def test_decompose_returns_decomposition(self) -> None:
        result = self.decomposer.decompose("I need to leave my job because everyone wants me to fail.")
        assert isinstance(result, EpistemicDecomposition)
        assert result.user_statement.startswith("I need to leave")
        assert len(result.layers) > 0

    def test_decompose_includes_interpretation_layer(self) -> None:
        result = self.decomposer.decompose("I need to leave my job because everyone wants me to fail.")
        layer_types = [layer.layer for layer in result.layers]
        assert "interpretation" in layer_types

    def test_interpretive_layers_have_alternatives(self) -> None:
        result = self.decomposer.decompose("I need to leave my job because everyone wants me to fail.")
        for layer in result.layers:
            if layer.layer in {"interpretation", "desire", "fear", "value", "narrative"}:
                assert len(layer.alternative_hypotheses) >= 1, (
                    f"Layer {layer.layer} must have at least one alternative hypothesis"
                )

    def test_every_layer_has_epistemic_status(self) -> None:
        result = self.decomposer.decompose("Some statement about my life.")
        for layer in result.layers:
            assert isinstance(layer.epistemic_status, EpistemicStatus)

    def test_fallback_on_malformed_output(self) -> None:
        """When the LLM fails, Aletheia returns an honest UNKNOWN decomposition."""

        class BrokenProvider(MockProvider):
            def complete(self, request):  # type: ignore[override]
                from aletheia.llm.base import LLMResponse
                return LLMResponse(text="not json at all", model="broken")

        decomposer = EpistemicDecomposer(llm=BrokenProvider())
        result = decomposer.decompose("Test statement.")
        assert isinstance(result, EpistemicDecomposition)
        assert len(result.layers) >= 1
        # Fallback layers must be UNKNOWN, never fabricated
        for layer in result.layers:
            assert layer.epistemic_status == EpistemicStatus.UNKNOWN
        assert any("Fallback" in n for n in result.notes)

    def test_render_produces_text(self) -> None:
        result = self.decomposer.decompose("Test.")
        rendered = self.decomposer.render(result)
        assert "Epistemic Decomposition" in rendered
        assert "OBSERVATION" in rendered or "INTERPRETATION" in rendered
