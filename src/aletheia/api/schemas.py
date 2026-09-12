"""Pydantic schemas for the HTTP API."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..core.types import ReflectionRequest


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
    wisdom_graph: dict[str, int]


class WisdomStatsResponse(BaseModel):
    traditions: int
    concepts: int
    claims: int


class DecomposeRequest(BaseModel):
    statement: str = Field(..., min_length=1, max_length=10_000)


class DecomposeResponse(BaseModel):
    user_statement: str
    layers: list[dict]
    notes: list[str]


class SocraticRequest(BaseModel):
    statement: str = Field(..., min_length=1, max_length=10_000)
    max_questions: int | None = Field(default=3, ge=1, le=8)


class SocraticResponse(BaseModel):
    questions: list[dict]


# Re-export ReflectionRequest for the API surface
__all__ = [
    "DecomposeRequest",
    "DecomposeResponse",
    "HealthResponse",
    "ReflectionRequest",
    "SocraticRequest",
    "SocraticResponse",
    "WisdomStatsResponse",
]
