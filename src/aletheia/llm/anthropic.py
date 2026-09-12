"""Anthropic Claude provider."""
from __future__ import annotations

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMProvider, LLMRequest, LLMResponse

log = structlog.get_logger(__name__)


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", timeout: int = 120):
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError(
                "The `anthropic` package is not installed. "
                "Install with: pip install aletheia-ai[anthropic]"
            ) from e
        self.client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        self.model = model

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def complete(self, request: LLMRequest) -> LLMResponse:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=request.max_tokens or 2048,
            temperature=request.temperature,
            system=request.system_prompt,
            messages=[{"role": "user", "content": request.user_prompt}],
        )
        text = resp.content[0].text if resp.content else ""
        return LLMResponse(
            text=text,
            model=self.model,
            usage={
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
            raw=resp.model_dump() if hasattr(resp, "model_dump") else None,
        )
