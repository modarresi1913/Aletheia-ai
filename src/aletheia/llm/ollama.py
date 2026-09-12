"""Ollama LLM provider (default open-source reference implementation).

Requires the `ollama` Python package (install with `pip install aletheia-ai[ollama]`)
and a running Ollama server (https://ollama.ai).

Quickstart:
    ollama pull llama3.1:8b-instruct-q5_K_M
    ollama serve   # or run via docker-compose
"""
from __future__ import annotations

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..core.config import get_settings
from .base import LLMProvider, LLMRequest, LLMResponse

log = structlog.get_logger(__name__)


class OllamaProvider(LLMProvider):
    """Synchronous Ollama provider with retry and JSON-mode support."""

    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        temperature: float | None = None,
        num_ctx: int | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.temperature = temperature if temperature is not None else settings.ollama_temperature
        self.num_ctx = num_ctx or settings.ollama_num_ctx
        self._client = None  # lazy

    def _ensure_client(self):
        if self._client is None:
            try:
                import ollama  # type: ignore[import-not-found]
            except ImportError as e:
                raise RuntimeError(
                    "The `ollama` package is not installed. "
                    "Install with: pip install aletheia-ai[ollama]"
                ) from e
            self._client = ollama.Client(host=self.base_url, timeout=self.timeout)
        return self._client

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
    )
    def complete(self, request: LLMRequest) -> LLMResponse:
        client = self._ensure_client()
        log.debug(
            "ollama.complete.start",
            model=self.model,
            json_mode=request.json_mode,
            prompt_len=len(request.user_prompt),
        )

        options = {
            "temperature": request.temperature,
            "num_ctx": self.num_ctx,
        }
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens

        # Ollama supports `format="json"` for structured output.
        fmt = "json" if request.json_mode else ""

        try:
            response = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                options=options,
                format=fmt or None,
            )
        except Exception as e:
            log.error("ollama.complete.error", error=str(e))
            raise

        text = response["message"]["content"] if isinstance(response, dict) else response.message.content
        usage = response.get("prompt_eval_count", None) if isinstance(response, dict) else None

        return LLMResponse(
            text=text,
            model=self.model,
            usage={"prompt_tokens": usage} if usage is not None else None,
            raw=response,
        )

    async def complete_async(self, request: LLMRequest) -> LLMResponse:
        """Async path uses Ollama's async client."""
        try:
            import ollama  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError(
                "The `ollama` package is not installed. "
                "Install with: pip install aletheia-ai[ollama]"
            ) from e

        client = ollama.AsyncClient(host=self.base_url, timeout=self.timeout)
        options = {
            "temperature": request.temperature,
            "num_ctx": self.num_ctx,
        }
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        fmt = "json" if request.json_mode else None

        response = await client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            options=options,
            format=fmt,
        )
        text = response["message"]["content"] if isinstance(response, dict) else response.message.content
        return LLMResponse(text=text, model=self.model, raw=response)
