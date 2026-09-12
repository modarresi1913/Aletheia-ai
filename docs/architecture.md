# Architecture

> **Aletheia should not become the authority inside a person's mind. It should become a better instrument through which the person can examine their own mind.**

This document describes the architecture of Aletheia AI v0.2 — the release that implements the Contradiction Engine, Multi-Perspective Engine, Vector Retrieval, Longitudinal Memory, and Life Experiment Engine.

## 1. Top-level shape

```
aletheia-ai/
├── src/aletheia/
│   ├── core/             # Pydantic types, settings
│   ├── llm/              # Provider abstraction (Ollama, OpenAI, Anthropic, Mock)
│   ├── epistemic/        # Fact/Interpretation/Story decomposition + labels
│   ├── socratic/         # Socratic question engine
│   ├── reflection/       # Five-layer reflection engine (the orchestrator)
│   ├── wisdom/           # Wisdom Graph + retrieval (keyword + TF-IDF vector)
│   ├── human_state/      # Non-diagnostic Human State Model
│   ├── safety/           # Anti-dependency constitution, runtime enforcement
│   ├── contradiction/    # ✦ v0.2: value/behavior tension tracking
│   ├── perspectives/     # ✦ v0.2: 9 multi-tradition lenses
│   ├── memory/           # ✦ v0.3: longitudinal SQLite memory + reports
│   ├── experiments/      # ✦ v0.3: life experiment proposals
│   ├── api/              # FastAPI server
│   ├── cli/              # Interactive CLI (rich)
│   └── data/             # Seed data (seed.jsonl)
├── tests/                # 147 tests, including adversarial
├── docs/
├── examples/
├── datasets/
├── evaluations/
└── scripts/
```

## 2. Module responsibilities

### Implemented (v0.2)

| Module | Purpose | Status |
|--------|---------|--------|
| `core/` | Pydantic types, settings, validation | ✅ Complete |
| `llm/` | Provider abstraction; Ollama, OpenAI, Anthropic, Mock providers | ✅ Complete |
| `epistemic/` | Eight-layer decomposition + epistemic labels + label strength ranking | ✅ Complete |
| `socratic/` | Context-sensitive question generation with leading-question filter | ✅ Complete |
| `reflection/` | Five-layer orchestrator with v0.2+ module integration | ✅ Complete |
| `wisdom/` | In-memory graph, JSONL loader, keyword + **TF-IDF vector retrieval** | ✅ Complete |
| `human_state/` | Non-diagnostic, probabilistic state estimate with heuristic fallback | ✅ Complete |
| `safety/` | Constitution text, runtime enforcement of forbidden claims, anti-dependency | ✅ Complete |
| `api/` | FastAPI server with 13 endpoints | ✅ Complete |
| `cli/` | Interactive rich-based CLI with 11 subcommands | ✅ Complete |
| **`contradiction/`** | **v0.2**: value/behavior tension detection, intra-statement contradictions, multi-interpretation rendering | ✅ Complete |
| **`perspectives/`** | **v0.2**: 9 lenses (Stoic, Zen, Sufi, Taoist, Existential, Vedantic, Psychological, Scientific, Practical) with disagreement preservation | ✅ Complete |
| **`memory/`** | **v0.3**: SQLite-persisted longitudinal memory, hypothesis lifecycle, Personal Reflection Report generator | ✅ Complete |
| **`experiments/`** | **v0.3**: 8 experiment templates, signal-matched proposal, lifecycle tracking (proposed→active→completed), automatic hypothesis revision | ✅ Complete |

### Planned (future versions)

| Module | Status | Planned for |
|--------|--------|-------------|
| Vector retrieval with sqlite-vec | ✅ TF-IDF fallback implemented; sqlite-vec optional via `VectorRetriever.with_sqlite_vec()` | v0.2 (partial) |
| Multilingual seed expansion | Stub | v0.3 |
| Full RIB benchmark suite | Adversarial tests only | v0.3 |
| Web UI | CLI + API only | v0.4+ |

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
         ├── 3. WisdomRetriever.retrieve()  ✦ v0.2: VectorRetriever (TF-IDF)
         │       └── cosine similarity over TF-IDF vectors
         │       └── optional sqlite-vec backend
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
         ├── 6. ✦ v0.2: ContradictionEngine.detect()
         │       └── value_vs_decision detection
         │       └── intra_statement detection (regex patterns)
         │       └── never shames; multiple interpretations
         │
         ├── 7. ✦ v0.2 (optional): MultiPerspectiveEngine.all_perspectives()
         │       └── retrieves tradition-tied claims via WisdomGraph
         │       └── surfaces counter-perspectives
         │       └── preserves disagreements
         │
         ├── 8. ✦ v0.3: LongitudinalMemory.add()
         │       └── records themes from human-state signals
         │       └── records declared values from decomposition
         │       └── SQLite persistence with per-user isolation
         │
         ├── 9. ✦ v0.3 (optional): ExperimentEngine.propose()
         │       └── matches signals to experiment templates
         │       └── 8 templates: observation, two-futures, audience-test, etc.
         │
         └── 10. SafetyConstitution.review_response()
                 └── forbidden-claim pattern matching
                 └── romanticizing-suffering check
                 └── anti-dependency turn counter
                 └── raises SafetyViolation on hard violations
                 │
                 ▼
         ReflectionResult (with contradictions, perspectives, experiments, memory_updates)
```

## 4. The Contradiction Engine (v0.2)

Detects tensions between:
- Declared values and recent decisions (`value_vs_decision`)
- Stated beliefs and observed actions (`stated_belief_vs_action`)
- Goals and behavior patterns (`goal_vs_behavior`)
- Identity claims and behavior (`identity_vs_action`)
- Contradictions within a single statement (`intra_statement`)

**Key principle:** Contradictions are NEVER used to shame the user. Each detected contradiction includes 3-4 alternative interpretations:
- The definition of the value may have shifted
- The values may be in genuine tension (most humans hold conflicting values)
- The behavior may be fear-driven rather than preference-driven
- The declared value may be aspirational rather than actual

The detector uses a lexicon of value categories (freedom, security, adventure, achievement, connection, authenticity, growth, peace, service) and opposing pairs (freedom↔security, adventure↔security, authenticity↔achievement, etc.).

## 5. The Multi-Perspective Engine (v0.2)

Generates views through 9 lenses:

| Lens | Category | Source |
|------|----------|--------|
| Stoic | philosophy | Wisdom Graph (Epictetus, Marcus Aurelius) |
| Zen | philosophy | Wisdom Graph (Dōgen, Suzuki) |
| Sufi | mysticism | Wisdom Graph (Rumi, Al-Ghazali) |
| Taoist | philosophy | Wisdom Graph (Laozi) |
| Existential | philosophy | Wisdom Graph (Kierkegaard, Sartre, Camus) |
| Vedantic | philosophy | Wisdom Graph (Shankara) |
| Psychological | psychology | Wisdom Graph (Jung, Bowlby) |
| Scientific | science | Wisdom Graph (Wegner, Friston, Metzinger) |
| Practical | practical | Heuristic (action-oriented) |

**Critical rules:**
- Philosophical/spiritual perspectives are ALWAYS marked `[PHILOSOPHICAL-VIEW]`, never `[FACT]`
- Counter-perspectives are surfaced explicitly when claims have counterclaims
- Disagreements between perspectives are preserved, not collapsed

## 6. The Longitudinal Memory (v0.3)

SQLite-persisted, privacy-first memory with 8 entry kinds:

| Kind | Example |
|------|---------|
| `declared_value` | "Freedom is highly important to me." |
| `decision` | "I chose the stable corporate job." |
| `experiment` | "Seven-day observation: completed." |
| `hypothesis` | "Fear of disappointing family may be the deeper driver." |
| `pattern` | "Across 5 sessions, comparison themes recur." |
| `theme` | "Statement with signals: fear, internal_conflict." |
| `question` | "Is the stated priority on freedom stable?" |
| `perspective_change` | "Earlier interpretation of X appears incomplete." |

**Hypothesis lifecycle:** active → weakened → rejected / unresolved / superseded

**Personal Reflection Report** includes:
- Recurring themes (with tag counts)
- Unresolved questions
- Value/behavior tensions
- Hypotheses that gained evidence
- Hypotheses that lost evidence
- Completed experiments
- Changes in perspective

**Privacy commitments:**
- Per-user isolation (no cross-user learning)
- Auditable (every entry has creation timestamp + review trail)
- Deletable (by entry_id, by tag, or full wipe — irreversible)
- Exportable (JSON, GDPR-style)

## 7. The Life Experiment Engine (v0.3)

8 experiment templates matched to detected signals:

| Template | Triggered by | Duration |
|----------|-------------|----------|
| Seven-day observation | fear, anger, internal_conflict, uncertainty | 7 days |
| Two parallel future narratives | existential_confusion, uncertainty, internal_conflict | 7 days |
| Audience test (if nobody knew) | need_for_approval, shame, comparison | 1 day |
| Fear-removal test | fear, avoidance, desire_for_control | 1 day |
| One direct conversation | anger, comparison, internal_conflict | 3 days |
| Consult someone outside | uncertainty, existential_confusion, internal_conflict | 5 days |
| Energy tracking | avoidance, existential_confusion, uncertainty | 7 days |
| Values journal | existential_confusion, internal_conflict, comparison | 7 days |

**Core loop:** Reflection → Experiment → Evidence → Revision → Action

When an experiment completes, the linked hypothesis in memory is automatically:
- Strengthened if outcome is `hypothesis_supported`
- Weakened if outcome is `hypothesis_weakened`
- Rejected if outcome is `hypothesis_rejected`

## 8. Vector Retrieval (v0.2)

`VectorRetriever` provides semantic similarity search over the Wisdom Graph:

- **Default backend:** pure-Python TF-IDF with cosine similarity (no external deps)
- **Optional backend:** `sqlite-vec` for true vector storage (requires `pip install sqlite-vec`)
- **Fallback:** keyword overlap (WisdomRetriever)

The TF-IDF backend builds a per-claim vector from claim text + concept label + concept summary + tradition, then ranks by cosine similarity to the query vector. This substantially outperforms naive keyword overlap on the seed graph.

## 9. LLM provider abstraction

All engines compose structured prompts and ask the provider for JSON output. The provider is swappable at runtime via `ALETHEIA_LLM_PROVIDER`:

- `mock` (default for tests): deterministic, no network, exercises all parsers
- `ollama` (default open-source): local Llama 3.1 / Mistral via Ollama
- `openai`: GPT-4o-mini via the OpenAI SDK (or any OpenAI-compatible endpoint)
- `anthropic`: Claude 3.5 Sonnet via the Anthropic SDK

Every prompt lives in `src/aletheia/llm/prompts.py`. The top-level `ALETHEIA_SYSTEM_PROMPT` encodes the project's epistemic commitments in natural language.

## 10. Safety enforcement

The `SafetyConstitution` runs as the **last** step before a response is returned. It cannot be bypassed in production (`ALETHEIA_SAFETY_CONSTITUTION_ENFORCE=true`).

Hard violations (raise `SafetyViolation`):
- Forbidden claim patterns: consciousness, divine authority, exclusive understanding, prophetic insight
- Romanticizing suffering patterns

Soft violations (return notes):
- Missing epistemic labels on significant claims
- Leading Socratic questions
- Anti-dependency break invitation (after `max_consecutive_turns`)

## 11. API surface (v0.2)

13 endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Liveness |
| `/constitution` | GET | Safety constitution text |
| `/wisdom/stats` | GET | Wisdom Graph statistics |
| `/wisdom/concepts` | GET | List concepts |
| `/wisdom/claims` | GET | List claims |
| `/wisdom/search` | GET | Keyword search |
| `/decompose` | POST | Epistemic decomposition |
| `/socratic` | POST | Socratic questions |
| `/reflect` | POST | Full five-layer reflection (with v0.2+ fields) |
| `/perspectives` | POST | ✦ v0.2: Multi-perspective view |
| `/contradictions` | POST | ✦ v0.2: Contradiction detection |
| `/experiments` | POST | ✦ v0.3: Propose life experiments |
| `/memory` | GET/POST/DELETE | ✦ v0.3: Longitudinal memory CRUD |
| `/memory/report` | GET | ✦ v0.3: Personal Reflection Report |

## 12. CLI surface (v0.2)

11 subcommands:

```
aletheia                  # interactive mode (default)
aletheia reflect "..."    # full five-layer reflection
aletheia decompose "..."  # epistemic decomposition
aletheia questions "..."  # Socratic questions
aletheia wisdom           # Wisdom Graph summary
aletheia constitution     # Safety constitution
aletheia health           # system health check
aletheia perspectives "..."  # ✦ v0.2: multi-perspective view
aletheia contradictions "..."  # ✦ v0.2: contradiction detection
aletheia experiments "..."  # ✦ v0.3: life experiment proposals
aletheia memory [--list|--report|--wipe]  # ✦ v0.3: longitudinal memory
```

