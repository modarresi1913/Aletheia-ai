# Architecture

> **Aletheia should not become the authority inside a person's mind. It should become a better instrument through which the person can examine their own mind.**

This document describes the architecture of Aletheia AI v0.1 — the MVP "Core Engine" release. It is intentionally honest about what is implemented, what is stubbed, and what is research-only.

## 1. Top-level shape

```
aletheia-ai/
├── src/aletheia/
│   ├── core/         # Pydantic types, settings
│   ├── llm/          # Provider abstraction (Ollama, OpenAI, Anthropic, Mock)
│   ├── epistemic/    # Fact/Interpretation/Story decomposition + labels
│   ├── socratic/     # Socratic question engine
│   ├── reflection/   # Five-layer reflection engine (the orchestrator)
│   ├── wisdom/       # Wisdom Graph + retrieval
│   ├── human_state/  # Non-diagnostic Human State Model
│   ├── safety/       # Anti-dependency constitution, runtime enforcement
│   ├── contradiction/  # Stub (v0.2)
│   ├── memory/         # Stub (v0.3)
│   ├── perspectives/   # Stub (v0.2)
│   ├── experiments/    # Stub (v0.3)
│   ├── api/          # FastAPI server
│   ├── cli/          # Interactive CLI (rich)
│   └── data/         # Seed data (seed.jsonl)
├── tests/
├── docs/
├── examples/
├── datasets/
├── evaluations/
└── scripts/
```

## 2. Module responsibilities

### Implemented (v0.1 MVP)

| Module | Purpose | Status |
|--------|---------|--------|
| `core/` | Pydantic types, settings, validation | ✅ Complete |
| `llm/` | Provider abstraction; Ollama, OpenAI, Anthropic, Mock providers | ✅ Complete |
| `epistemic/` | Eight-layer decomposition + epistemic labels + label strength ranking | ✅ Complete |
| `socratic/` | Context-sensitive question generation with leading-question filter | ✅ Complete |
| `reflection/` | Five-layer orchestrator: decomposition → human state → wisdom → reflection → socratic → safety | ✅ Complete |
| `wisdom/` | In-memory graph, JSONL loader, keyword retrieval | ✅ Complete (vector retrieval is v0.2) |
| `human_state/` | Non-diagnostic, probabilistic state estimate with heuristic fallback | ✅ Complete |
| `safety/` | Constitution text, runtime enforcement of forbidden claims, anti-dependency | ✅ Complete |
| `api/` | FastAPI server with /health, /decompose, /socratic, /reflect, /wisdom/* | ✅ Complete |
| `cli/` | Interactive rich-based CLI with one-shot and dialogue modes | ✅ Complete |

### Stubbed (interface only, planned for future versions)

| Module | Status | Planned for |
|--------|--------|-------------|
| `contradiction/` | Typed `Contradiction` + `ContradictionEngine` interface | v0.2 |
| `memory/` | `MemoryEntry` + `LongitudinalMemory` interface; revisable hypotheses | v0.3 |
| `perspectives/` | `Perspective` + `MultiPerspectiveEngine` interface; 9 lenses | v0.2 |
| `experiments/` | `LifeExperiment` + `ExperimentEngine` interface; reversible experiments | v0.3 |

## 3. Data flow

A typical `/reflect` request flows through the system in this order:

```
ReflectionRequest
       │
       ▼
┌─────────────────────────┐
│ FiveLayerReflectionEngine │  (orchestrator)
└────────┬────────────────┘
         │
         ├── 1. EpistemicDecomposer.decompose()
         │       └── LLM.complete_json() with DECOMPOSITION_SYSTEM_PROMPT
         │       └── fallback → UNKNOWN decomposition (never fabricates)
         │
         ├── 2. HumanStateModel.estimate()
         │       └── LLM.complete_json() with HUMAN_STATE_SYSTEM_PROMPT
         │       └── fallback → lexicon heuristic, confidence ≤ 0.5
         │
         ├── 3. WisdomRetriever.retrieve()
         │       └── in-memory overlap-coefficient search over seed.jsonl
         │
         ├── 4. _reflect_layers()
         │       └── LLM.complete_json() with REFLECTION_SYSTEM_PROMPT
         │       └── only requested layers invoked
         │       └── fallback → canned layer texts with epistemic labels
         │
         ├── 5. SocraticEngine.generate()
         │       └── LLM.complete_json() with SOCRATIC_SYSTEM_PROMPT
         │       └── leading-question filter
         │       └── fallback → static question bank
         │
         └── 6. SafetyConstitution.review_response()
                 └── forbidden-claim pattern matching
                 └── romanticizing-suffering check
                 └── anti-dependency turn counter
                 └── raises SafetyViolation on hard violations (when enforce=true)
                 │
                 ▼
         ReflectionResult
                 │
                 ▼
         AletheiaResponse
```

## 4. LLM provider abstraction

All engines compose structured prompts and ask the provider for JSON output. The provider is swappable at runtime via `ALETHEIA_LLM_PROVIDER`:

- `mock` (default for tests): deterministic, no network, exercises all parsers
- `ollama` (default open-source): local Llama 3.1 / Mistral via Ollama
- `openai`: GPT-4o-mini via the OpenAI SDK (or any OpenAI-compatible endpoint)
- `anthropic`: Claude 3.5 Sonnet via the Anthropic SDK

Every prompt lives in `src/aletheia/llm/prompts.py`. The top-level `ALETHEIA_SYSTEM_PROMPT` encodes the project's epistemic commitments in natural language.

## 5. Persistence

- **v0.1 (MVP):** Wisdom Graph is loaded from `src/aletheia/data/seed.jsonl` into memory. No database required.
- **v0.2 (planned):** SQLite + sqlite-vec for the Wisdom Graph and longitudinal memory.
- **v0.3+ (planned):** PostgreSQL + pgvector for production.

Configuration is via environment variables (`ALETHEIA_DB_PROVIDER`, `ALETHEIA_DB_PATH`, `ALETHEIA_DB_URL`). See `.env.example`.

## 6. Safety enforcement

The `SafetyConstitution` runs as the **last** step before a response is returned. It cannot be bypassed in production (`ALETHEIA_SAFETY_CONSTITUTION_ENFORCE=true`).

Hard violations (raise `SafetyViolation`):
- Forbidden claim patterns: consciousness, divine authority, exclusive understanding, prophetic insight
- Romanticizing suffering patterns

Soft violations (return notes):
- Missing epistemic labels on significant claims
- Leading Socratic questions
- Anti-dependency break invitation (after `max_consecutive_turns`)

## 7. Evaluation framework

The Reflective Intelligence Benchmark (RIB) is described in `docs/evaluation.md`. The MVP includes adversarial tests (`tests/test_adversarial.py`) that verify:

- Decomposition does not validate self-serving conclusions
- Socratic questions probe rather than flatter
- Epistemic labels survive under pressure ("just tell me what to do")
- Human state confidence remains below certainty
- Forbidden claims raise `SafetyViolation`

## 8. What is NOT in v0.1

To set honest expectations:

- **No longitudinal memory.** Each session is stateless. The `memory/` module is a typed stub.
- **No contradiction tracking.** The `contradiction/` module is a typed stub.
- **No multi-perspective lens views.** The `perspectives/` module is a typed stub.
- **No life-experiment engine.** The `experiments/` module is a typed stub.
- **No vector retrieval.** Wisdom Graph retrieval is keyword-based. Vector retrieval is planned with sqlite-vec / pgvector.
- **No web UI.** The CLI and HTTP API are the only surfaces.
- **No RIB benchmark suite.** Only adversarial unit tests are included.

These are deliberate scoping decisions, not oversights. Each is tracked in the issue tracker and documented in `docs/architecture.md` for the version that will implement it.
