"""Tests for the core type system."""
from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from aletheia.core.types import (
    Confidence,
    ConfidenceField,
    EpistemicStatus,
    HumanStateEstimate,
    HumanStateSignal,
    ReflectionLayer,
    validate_confidence,
)


class TestEpistemicStatus:
    def test_seven_statuses_exist(self) -> None:
        expected = {
            "FACT", "EVIDENCE-SUPPORTED", "PLAUSIBLE", "INTERPRETATION",
            "PHILOSOPHICAL-VIEW", "SPECULATION", "UNKNOWN",
        }
        actual = {s.value for s in EpistemicStatus}
        assert actual == expected


class TestConfidence:
    def test_constructs_as_float(self) -> None:
        assert float(Confidence(0.0)) == 0.0
        assert float(Confidence(0.5)) == 0.5
        assert float(Confidence(1.0)) == 1.0

    def test_validate_confidence_rejects_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            validate_confidence(1.5)
        with pytest.raises(ValueError):
            validate_confidence(-0.1)

    def test_pydantic_field_validates_range(self) -> None:
        class M(BaseModel):
            c: ConfidenceField

        # Valid
        assert M(c=0.5).c == 0.5
        # Out of range -> rejected by Pydantic
        with pytest.raises(ValidationError):
            M(c=1.5)
        with pytest.raises(ValidationError):
            M(c=-0.1)


class TestHumanStateEstimate:
    def test_confidence_capped_below_certainty(self) -> None:
        # Confidence of 0.95 or higher must be rejected
        with pytest.raises(ValidationError):
            HumanStateEstimate(
                primary_signals=[HumanStateSignal.FEAR],
                confidence=0.95,
            )
        with pytest.raises(ValidationError):
            HumanStateEstimate(
                primary_signals=[HumanStateSignal.FEAR],
                confidence=0.99,
            )

    def test_valid_estimate(self) -> None:
        e = HumanStateEstimate(
            primary_signals=[HumanStateSignal.FEAR, HumanStateSignal.UNCERTAINTY],
            confidence=0.45,
            alternative_signals=[HumanStateSignal.ANGER],
        )
        assert e.confidence == 0.45
        assert HumanStateSignal.FEAR in e.primary_signals


class TestReflectionLayer:
    def test_five_layers_exist(self) -> None:
        expected = {"epistemic", "psychological", "practical", "ethical", "existential"}
        actual = {layer.value for layer in ReflectionLayer}
        assert actual == expected
