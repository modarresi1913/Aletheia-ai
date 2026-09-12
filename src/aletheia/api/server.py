"""Aletheia FastAPI server.

Endpoints:
    GET  /health           — liveness
    GET  /constitution     — view the safety constitution
    GET  /wisdom/stats     — Wisdom Graph statistics
    POST /decompose        — epistemic decomposition only
    POST /socratic         — generate Socratic questions
    POST /reflect          — full five-layer reflection
    GET  /wisdom/concepts  — list concepts in the Wisdom Graph
    GET  /wisdom/claims     — list claims in the Wisdom Graph
"""
from __future__ import annotations

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..core.config import get_settings
from ..core.types import (
    AletheiaResponse,
    EpistemicStatus,
    ReflectionRequest,
    ReflectionResult,
)
from ..epistemic.decomposition import EpistemicDecomposer
from ..human_state.model import HumanStateModel
from ..reflection.five_layer import FiveLayerReflectionEngine
from ..safety.constitution import SafetyConstitution, SafetyViolation
from ..socratic.engine import SocraticEngine
from ..wisdom.graph import WisdomGraph
from ..wisdom.retrieval import WisdomRetriever
from .schemas import (
    DecomposeRequest,
    DecomposeResponse,
    HealthResponse,
    SocraticRequest,
    SocraticResponse,
    WisdomStatsResponse,
)

log = structlog.get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title="Aletheia AI",
    description=(
        "An experimental Reflective Intelligence architecture for epistemic clarity, "
        "self-understanding, and autonomous human choice."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Shared engine instances ───────────────────────────────────
# These are constructed once and reused across requests.
_safety = SafetyConstitution()
_decomposer = EpistemicDecomposer()
_socratic_engine = SocraticEngine()
_human_state = HumanStateModel()
_wisdom_graph = WisdomGraph.default()
_wisdom_retriever = WisdomRetriever(_wisdom_graph)
_reflection_engine = FiveLayerReflectionEngine(
    decomposer=_decomposer,
    socratic=_socratic_engine,
    human_state_model=_human_state,
    wisdom_graph=_wisdom_graph,
    wisdom_retriever=_wisdom_retriever,
    safety=_safety,
)


# ── Health & meta ─────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="0.1.0",
        llm_provider=settings.llm_provider,
        wisdom_graph=_wisdom_graph.stats(),
    )


@app.get("/constitution", tags=["meta"])
async def constitution() -> dict[str, str]:
    return {"text": _safety.text()}


# ── Wisdom Graph ──────────────────────────────────────────────

@app.get("/wisdom/stats", response_model=WisdomStatsResponse, tags=["wisdom"])
async def wisdom_stats() -> WisdomStatsResponse:
    return WisdomStatsResponse(**_wisdom_graph.stats())


@app.get("/wisdom/concepts", tags=["wisdom"])
async def wisdom_concepts() -> list[dict]:
    return [c.model_dump() for c in _wisdom_graph.all_concepts()]


@app.get("/wisdom/claims", tags=["wisdom"])
async def wisdom_claims() -> list[dict]:
    return [c.model_dump() for c in _wisdom_graph.all_claims()]


@app.get("/wisdom/search", tags=["wisdom"])
async def wisdom_search(q: str, top_k: int = 3) -> list[dict]:
    claims = _wisdom_retriever.retrieve(q, top_k=top_k)
    return [c.model_dump() for c in claims]


# ── Epistemic decomposition ───────────────────────────────────

@app.post("/decompose", response_model=DecomposeResponse, tags=["epistemic"])
async def decompose(req: DecomposeRequest) -> DecomposeResponse:
    try:
        d = _decomposer.decompose(req.statement)
        return DecomposeResponse(
            user_statement=d.user_statement,
            layers=[layer.model_dump() for layer in d.layers],
            notes=d.notes,
        )
    except Exception as e:
        log.error("api.decompose.error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Socratic ──────────────────────────────────────────────────

@app.post("/socratic", response_model=SocraticResponse, tags=["socratic"])
async def socratic(req: SocraticRequest) -> SocraticResponse:
    try:
        questions = _socratic_engine.generate(
            req.statement, max_questions=req.max_questions or 3
        )
        return SocraticResponse(
            questions=[q.model_dump() for q in questions],
        )
    except Exception as e:
        log.error("api.socratic.error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Full reflection ───────────────────────────────────────────

@app.post("/reflect", response_model=AletheiaResponse, tags=["reflection"])
async def reflect(req: ReflectionRequest) -> AletheiaResponse:
    try:
        result: ReflectionResult = _reflection_engine.reflect(
            user_statement=req.statement,
            requested_layers=req.requested_layers,
            conversation_history=req.conversation_history,
            max_questions=req.max_questions,
        )

        # Build the surface text the user would see
        surface_parts: list[str] = []
        for layer_name, text in result.layer_outputs.items():
            surface_parts.append(f"{layer_name.upper()}\n{text}\n")
        if result.socratic_questions:
            surface_parts.append("QUESTIONS FOR YOU")
            for i, q in enumerate(result.socratic_questions, 1):
                surface_parts.append(f"{i}. {q.text}")
        if result.safety_notes:
            surface_parts.append("\nNOTES")
            for n in result.safety_notes:
                surface_parts.append(f"- {n}")
        surface_text = "\n".join(surface_parts)

        # Determine overall epistemic status (weakest layer wins)
        overall_status = EpistemicStatus.UNKNOWN
        for layer in result.decomposition.layers:
            # weaker status wins
            from ..epistemic.labels import status_rank
            if status_rank(layer.epistemic_status) < status_rank(overall_status) or overall_status == EpistemicStatus.UNKNOWN:
                overall_status = layer.epistemic_status

        return AletheiaResponse(
            surface_text=surface_text,
            epistemic_status=overall_status,
            reflection=result,
            turn_number=len(req.conversation_history or []),
            invited_break=_safety.should_invite_break(len(req.conversation_history or [])),
        )
    except SafetyViolation as sv:
        log.error("api.reflect.safety_violation", rule=sv.rule, detail=sv.detail)
        raise HTTPException(status_code=500, detail=f"Safety violation: {sv.detail}") from sv
    except Exception as e:
        log.error("api.reflect.error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Entrypoint ────────────────────────────────────────────────

def run() -> None:
    """Run the API server with uvicorn."""
    import uvicorn

    uvicorn.run(
        "aletheia.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level,
        reload=False,
    )


if __name__ == "__main__":
    run()
