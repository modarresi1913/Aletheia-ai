"""Tests for the LLM provider abstraction."""
from __future__ import annotations

import pytest

from aletheia.llm.base import LLMRequest, get_llm_provider
from aletheia.llm.mock import MockProvider


class TestMockProvider:
    def test_name(self) -> None:
        assert MockProvider().name == "mock"

    def test_complete_returns_response(self) -> None:
        p = MockProvider()
        resp = p.complete(LLMRequest(system_prompt="Epistemic Decomposition component", user_prompt="test"))
        assert resp.text
        assert resp.model == "mock-0.1"

    def test_complete_json_parses(self) -> None:
        p = MockProvider()
        data = p.complete_json(
            LLMRequest(system_prompt="Epistemic Decomposition component", user_prompt="test")
        )
        assert isinstance(data, dict)
        assert "layers" in data

    def test_strips_code_fences(self) -> None:
        # Verify the as_json helper handles ```json fences
        from aletheia.llm.base import LLMResponse

        resp = LLMResponse(text="```json\n{\"a\": 1}\n```", model="test")
        assert resp.as_json() == {"a": 1}


class TestProviderFactory:
    def test_get_mock_provider(self) -> None:
        p = get_llm_provider("mock")
        assert isinstance(p, MockProvider)

    def test_get_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError):
            get_llm_provider("nonexistent_provider")

    def test_default_is_mock_in_tests(self) -> None:
        # conftest.py forces ALETHEIA_LLM_PROVIDER=mock
        p = get_llm_provider()
        assert isinstance(p, MockProvider)
