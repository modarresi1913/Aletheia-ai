"""Application configuration.

Settings are loaded from environment variables (and `.env` if present).
All defaults preserve the safety constitution.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for Aletheia.

    Defaults are deliberately conservative. The safety constitution is enforced
    at runtime regardless of configuration.
    """

    model_config = SettingsConfigDict(
        env_prefix="ALETHEIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── General ───────────────────────────────────────────────
    env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # ── LLM ───────────────────────────────────────────────────
    llm_provider: Literal["ollama", "openai", "anthropic", "mock"] = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b-instruct-q5_K_M"
    ollama_timeout: int = 120
    ollama_temperature: float = 0.4
    ollama_num_ctx: int = 8192
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # ── Database ──────────────────────────────────────────────
    db_provider: Literal["sqlite", "postgres"] = "sqlite"
    db_path: str = "./data/aletheia.db"
    db_url: str | None = None

    # ── Wisdom Graph ──────────────────────────────────────────
    wisdom_graph_seed: bool = True
    wisdom_graph_seed_path: str = "src/aletheia/data/seed.jsonl"

    # ── Reflection ────────────────────────────────────────────
    reflection_layers: str = "epistemic,psychological,practical,ethical,existential"
    decomposition_depth: int = 8

    # ── Safety ────────────────────────────────────────────────
    safety_constitution_enforce: bool = True
    safety_max_consecutive_turns: int = 12
    safety_forbidden_claims: str = (
        "consciousness,divine_authority,exclusive_understanding,prophetic_insight"
    )

    # ── API ───────────────────────────────────────────────────
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_log_level: str = "info"

    # ── Derived ───────────────────────────────────────────────
    @property
    def reflection_layer_list(self) -> list[str]:
        return [s.strip() for s in self.reflection_layers.split(",") if s.strip()]

    @property
    def forbidden_claims_list(self) -> list[str]:
        return [s.strip() for s in self.safety_forbidden_claims.split(",") if s.strip()]

    @field_validator("safety_max_consecutive_turns")
    @classmethod
    def _floor_max_turns(cls, v: int) -> int:
        if v < 4:
            raise ValueError("safety_max_consecutive_turns must be >= 4 (anti-dependency floor)")
        return v

    @field_validator("decomposition_depth")
    @classmethod
    def _bound_depth(cls, v: int) -> int:
        if not 1 <= v <= 8:
            raise ValueError("decomposition_depth must be in [1, 8]")
        return v

    def data_dir(self) -> Path:
        p = Path(self.db_path).resolve().parent
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Use this everywhere — do not construct."""
    return Settings()
