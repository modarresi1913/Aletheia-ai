"""Tests for the Socratic Engine."""
from __future__ import annotations

from aletheia.core.types import SocraticQuestion
from aletheia.llm.mock import MockProvider
from aletheia.socratic.engine import SocraticEngine


class TestSocraticEngine:
    def setup_method(self) -> None:
        self.engine = SocraticEngine(llm=MockProvider(), max_questions=3)

    def test_generate_returns_questions(self) -> None:
        qs = self.engine.generate("I'm thinking of leaving my job.")
        assert isinstance(qs, list)
        assert len(qs) >= 1
        for q in qs:
            assert isinstance(q, SocraticQuestion)
            assert len(q.text) > 10

    def test_questions_are_open(self) -> None:
        qs = self.engine.generate("Should I quit?")
        for q in qs:
            assert q.is_open, f"Question must be open-ended: {q.text!r}"

    def test_questions_target_a_layer(self) -> None:
        qs = self.engine.generate("I'm afraid of disappointing my parents.")
        layers_seen = {q.targeted_layer for q in qs}
        # At least one question must target a layer
        assert any(layer is not None for layer in layers_seen)

    def test_no_leading_questions(self) -> None:
        # The mock's canned questions are non-leading; this is also enforced
        # by the engine's filter, but the test ensures the filter works.
        from aletheia.socratic.engine import SocraticEngine as SE

        class LeadingProvider(MockProvider):
            def complete(self, request):  # type: ignore[override]
                import json

                from aletheia.llm.base import LLMResponse
                data = {
                    "questions": [
                        {
                            "text": "Don't you think you should leave?",
                            "purpose": "leading",
                            "targeted_layer": "psychological",
                            "epistemic_status": "INTERPRETATION",
                            "is_open": True,
                        },
                        {
                            "text": "What evidence would change your mind?",
                            "purpose": "good",
                            "targeted_layer": "epistemic",
                            "epistemic_status": "INTERPRETATION",
                            "is_open": True,
                        },
                    ]
                }
                return LLMResponse(text=json.dumps(data), model="leading")

        engine = SE(llm=LeadingProvider(), max_questions=3)
        qs = engine.generate("test")
        # The leading question must have been filtered out
        for q in qs:
            assert not q.text.lower().startswith("don't you think")

    def test_fallback_on_failure(self) -> None:
        class BrokenProvider(MockProvider):
            def complete(self, request):  # type: ignore[override]
                from aletheia.llm.base import LLMResponse
                return LLMResponse(text="not json", model="broken")

        engine = SocraticEngine(llm=BrokenProvider(), max_questions=3)
        qs = engine.generate("test")
        assert len(qs) >= 1
        for q in qs:
            assert q.text  # non-empty
