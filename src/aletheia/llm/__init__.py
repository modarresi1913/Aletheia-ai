"""LLM provider abstraction.

Aletheia treats the model provider as a swappable component. The interface is
intentionally narrow: a single `complete` method that takes a structured prompt
and returns a structured response.

Two reference implementations are provided:
- `OllamaProvider` (default, open-source, local)
- `MockProvider` (deterministic, for tests and offline development)

Optional providers (`OpenAIProvider`, `AnthropicProvider`) are loaded lazily
and require the corresponding optional dependency.
"""
from __future__ import annotations

from .base import LLMProvider, LLMRequest, LLMResponse, get_llm_provider
from .mock import MockProvider
from .prompts import (
    ALETHEIA_SYSTEM_PROMPT,
    DECOMPOSITION_SYSTEM_PROMPT,
    HUMAN_STATE_SYSTEM_PROMPT,
    REFLECTION_SYSTEM_PROMPT,
    SOCRATIC_SYSTEM_PROMPT,
)

__all__ = [
    "ALETHEIA_SYSTEM_PROMPT",
    "DECOMPOSITION_SYSTEM_PROMPT",
    "HUMAN_STATE_SYSTEM_PROMPT",
    "REFLECTION_SYSTEM_PROMPT",
    "SOCRATIC_SYSTEM_PROMPT",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "MockProvider",
    "get_llm_provider",
]
