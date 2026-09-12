"""Pydantic schemas for the HTTP API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..core.types import EpistemicStatus, ReflectionRequest


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


# ── v0.2 schemas ────────────────────────────────────────────────


class PerspectivesRequest(BaseModel):
    statement: str = Field(..., min_length=1, max_length=10_000)


class ContradictionsRequest(BaseModel):
    user_id: str = Field(default="anonymous")
    statement: str = Field(..., min_length=1, max_length=10_000)


# ── v0.3 schemas ────────────────────────────────────────────────


class ExperimentsRequest(BaseModel):
    user_id: str = Field(default="anonymous")
    statement: str = Field(..., min_length=1, max_length=10_000)
    signals: list[str] | None = None
    max_proposals: int | None = Field(default=3, ge=1, le=5)


MemoryKindLiteral = Literal[
    "declared_value", "decision", "experiment", "hypothesis",
    "pattern", "theme", "question", "perspective_change",
]


class MemoryAddRequest(BaseModel):
    user_id: str = Field(default="anonymous")
    kind: MemoryKindLiteral
    text: str = Field(..., min_length=1, max_length=5_000)
    epistemic_status: EpistemicStatus = EpistemicStatus.INTERPRETATION
    confidence: float = Field(default=0.4, ge=0.0, le=0.94)
    evidence: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


# Re-export ReflectionRequest for the API surface
__all__ = [
    "ContradictionsRequest",
    "DecomposeRequest",
    "DecomposeResponse",
    "ExperimentsRequest",
    "HealthResponse",
    "MemoryAddRequest",
    "PerspectivesRequest",
    "ReflectionRequest",
    "SocraticRequest",
    "SocraticResponse",
    "WisdomStatsResponse",
]
