"""LLM provider interface and factory.

The interface is deliberately minimal. Higher-level Aletheia modules compose
structured prompts; the provider only needs to turn a prompt into text.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..core.config import get_settings


@dataclass
class LLMRequest:
    """A single completion request."""

    system_prompt: str
    user_prompt: str
    temperature: float = 0.4
    max_tokens: int | None = None
    json_mode: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "json_mode": self.json_mode,
            "extra": self.extra,
        }


@dataclass
class LLMResponse:
    """A single completion response."""

    text: str
    model: str
    usage: dict[str, int] | None = None
    raw: Any = None

    def as_json(self) -> Any:
        """Parse the response as JSON. Raises if malformed."""
        t = self.text.strip()
        # Strip code fences if present
        if t.startswith("```"):
            first_newline = t.find("\n")
            if first_newline != -1:
                t = t[first_newline + 1:]
            if t.endswith("```"):
                t = t[: -3]
            t = t.strip()
        return json.loads(t)


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    name: str = "abstract"

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Synchronous completion. Override `complete_async` for async path."""
        ...

    async def complete_async(self, request: LLMRequest) -> LLMResponse:
        """Default async path delegates to sync. Override for true async."""
        return self.complete(request)

    def complete_json(self, request: LLMRequest) -> Any:
        """Complete and parse as JSON. Forces json_mode if supported."""
        request.json_mode = True
        return self.complete(request).as_json()


def get_llm_provider(provider: str | None = None) -> LLMProvider:
    """Return a provider instance based on settings or explicit override."""
    settings = get_settings()
    provider_name = provider or settings.llm_provider

    if provider_name == "mock":
        from .mock import MockProvider
        return MockProvider()
    if provider_name == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout,
            temperature=settings.ollama_temperature,
            num_ctx=settings.ollama_num_ctx,
        )
    if provider_name == "openai":
        from .openai_compat import OpenAIProvider
        if not settings.openai_api_key:
            raise RuntimeError("ALETHEIA_OPENAI_API_KEY is required when provider=openai")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
        )
    if provider_name == "anthropic":
        from .anthropic import AnthropicProvider
        if not settings.anthropic_api_key:
            raise RuntimeError("ALETHEIA_ANTHROPIC_API_KEY is required when provider=anthropic")
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )
    raise ValueError(f"Unknown LLM provider: {provider_name!r}")
