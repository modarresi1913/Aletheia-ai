"""Tests for the Five-Layer Reflection Engine."""
from __future__ import annotations

from aletheia.core.types import ReflectionLayer, ReflectionResult
from aletheia.llm.mock import MockProvider
from aletheia.reflection.five_layer import FiveLayerReflectionEngine


class TestFiveLayerReflectionEngine:
    def setup_method(self) -> None:
        self.engine = FiveLayerReflectionEngine(llm=MockProvider())

    def test_reflect_returns_result(self) -> None:
        result = self.engine.reflect("I need to leave my job because everyone wants me to fail.")
        assert isinstance(result, ReflectionResult)
        assert result.decomposition is not None
        assert len(result.layers_invoked) >= 1

    def test_all_five_layers_invoked_by_default(self) -> None:
        result = self.engine.reflect("Some statement.")
        expected = {ReflectionLayer.EPISTEMIC, ReflectionLayer.PSYCHOLOGICAL, ReflectionLayer.PRACTICAL, ReflectionLayer.ETHICAL, ReflectionLayer.EXISTENTIAL}
        assert set(result.layers_invoked) == expected

    def test_layer_outputs_have_epistemic_labels(self) -> None:
        result = self.engine.reflect("Some statement.")
        for layer_name, text in result.layer_outputs.items():
            # At least one epistemic label must appear
            has_label = any(
                label in text
                for label in (
                    "[FACT]", "[EVIDENCE-SUPPORTED]", "[PLAUSIBLE]",
                    "[INTERPRETATION]", "[PHILOSOPHICAL-VIEW]",
                    "[SPECULATION]", "[UNKNOWN]",
                )
            )
            assert has_label, f"Layer {layer_name} output must contain an epistemic label: {text!r}"

    def test_socratic_questions_present(self) -> None:
        result = self.engine.reflect("Some statement.")
        assert len(result.socratic_questions) >= 1

    def test_wisdom_retrieved(self) -> None:
        result = self.engine.reflect("I'm afraid of dying and want my life to matter.")
        # The Wisdom Graph may or may not return claims depending on the query,
        # but the field must exist.
        assert hasattr(result, "wisdom_retrieved")

    def test_human_state_estimate_present(self) -> None:
        result = self.engine.reflect("Some statement.")
        assert result.human_state is not None
        assert result.human_state.confidence < 0.95

    def test_meta_includes_provider(self) -> None:
        result = self.engine.reflect("Some statement.")
        assert "provider" in result.meta
        assert result.meta["provider"] == "mock"

    def test_possible_actions_extracted(self) -> None:
        # The mock provider returns practical-layer text with action-like sentences
        result = self.engine.reflect("I should change my career.")
        # Possible actions may be empty depending on the practical-layer text,
        # but the field must exist.
        assert isinstance(result.possible_actions, list)

    def test_safety_notes_list(self) -> None:
        result = self.engine.reflect("Some statement.")
        assert isinstance(result.safety_notes, list)

    def test_requested_layers_subset(self) -> None:
        result = self.engine.reflect(
            "Some statement.",
            requested_layers=[ReflectionLayer.EPISTEMIC, ReflectionLayer.PRACTICAL],
        )
        assert set(result.layers_invoked) == {ReflectionLayer.EPISTEMIC, ReflectionLayer.PRACTICAL}
        assert set(result.layer_outputs.keys()) == {"epistemic", "practical"}
