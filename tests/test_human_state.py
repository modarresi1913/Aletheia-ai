"""Tests for the Human State Model."""
from __future__ import annotations

from aletheia.core.types import HumanStateEstimate, HumanStateSignal
from aletheia.human_state.model import HumanStateModel
from aletheia.llm.mock import MockProvider


class TestHumanStateModel:
    def setup_method(self) -> None:
        self.model = HumanStateModel(llm=MockProvider())

    def test_estimate_returns_estimate(self) -> None:
        e = self.model.estimate("I'm scared and don't know what to do.")
        assert isinstance(e, HumanStateEstimate)
        assert len(e.primary_signals) >= 1

    def test_confidence_below_certainty(self) -> None:
        e = self.model.estimate("I'm scared and don't know what to do.")
        assert e.confidence < 0.95

    def test_alternatives_present_when_primary_nonempty(self) -> None:
        e = self.model.estimate("I'm scared and don't know what to do.")
        if e.primary_signals:
            assert len(e.alternative_signals) >= 1, (
                "When primary_signals is non-empty, alternative_signals must be present"
            )

    def test_fallback_heuristic_works(self) -> None:
        class BrokenProvider(MockProvider):
            def complete(self, request):  # type: ignore[override]
                from aletheia.llm.base import LLMResponse
                return LLMResponse(text="not json", model="broken")

        model = HumanStateModel(llm=BrokenProvider())
        e = model.estimate("I'm afraid of dying and confused about life")
        # Heuristic should pick up "afraid" -> FEAR, "confused" -> UNCERTAINTY
        assert isinstance(e, HumanStateEstimate)
        assert len(e.primary_signals) >= 1
        assert e.confidence <= 0.5  # heuristic path is capped

    def test_estimate_with_history(self) -> None:
        history = [
            {"role": "user", "content": "I'm worried about my job."},
            {"role": "assistant", "content": "What is your fear about specifically?"},
            {"role": "user", "content": "I'm afraid of being judged."},
        ]
        e = self.model.estimate("I think they all hate me.", conversation_history=history)
        assert isinstance(e, HumanStateEstimate)

    def test_only_known_signals_returned(self) -> None:
        e = self.model.estimate("test statement")
        for s in e.primary_signals + e.alternative_signals:
            assert isinstance(s, HumanStateSignal)
