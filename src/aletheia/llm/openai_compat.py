"""OpenAI-compatible provider.

Uses the `openai` Python SDK. Compatible with OpenAI's official API and any
OpenAI-compatible endpoint (e.g. vLLM, Together, Anyscale).
"""
from __future__ import annotations

import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from .base import LLMProvider, LLMRequest, LLMResponse

log = structlog.get_logger(__name__)


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        timeout: int = 120,
    ) -> None:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError(
                "The `openai` package is not installed. "
                "Install with: pip install aletheia-ai[openai]"
            ) from e
        kwargs: dict = {"api_key": api_key, "timeout": timeout}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def complete(self, request: LLMRequest) -> LLMResponse:
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = self.client.chat.completions.create(**kwargs)
        text = resp.choices[0].message.content or ""
        return LLMResponse(
            text=text,
            model=self.model,
            usage={
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
            raw=resp.model_dump() if hasattr(resp, "model_dump") else None,
        )
