<div align="center">

# 🪞 Aletheia AI

### *An AI architecture for truth-seeking, self-understanding, and autonomous human choice.*

---

### We taught machines to predict what humans say.
### Aletheia explores whether machines can help humans understand **why** they say it.

---

![Status](https://img.shields.io/badge/status-alpha_experiment-orange?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square)
![Tests](https://img.shields.io/badge/tests-84_passing-brightgreen?style=flat-square)
![Research](https://img.shields.io/badge/research-Reflective_Intelligence-purple?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-Ollama_OpenAI_Anthropic-9cf?style=flat-square)

**Reflective Intelligence Architecture** · **Epistemic Honesty by Design** · **Anti-Dependency Constitution**

</div>

---

> **Aletheia does not exist to tell humans what to think.**
> **It exists to help humans see what is thinking through them.**

---

## ✦ What is Aletheia?

**Aletheia** (from Greek ἀλήθεια — *"un-concealment"*) is an experimental, research-grade, open-source AI architecture for **epistemic clarity, self-understanding, and autonomous human choice**.

It is **NOT**:
- 🚫 Another chatbot
- 🚫 Another meditation app
- 🚫 Another AI therapist
- 🚫 Another RAG demo
- 🚫 A spiritual guru or life coach

It **IS** an architecture that makes **wisdom, uncertainty, contradiction, evidence, and human autonomy** computationally explicit — first-class objects in the type system, not afterthoughts in the prompt.

---

## ✦ The Thesis

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   Conventional AI:   prediction  →  generation  →  recommendation    │
│                                                                      │
│   Reflective AI:     observation  →  reflection                      │
│                                   →  epistemic clarification         │
│                                   →  hypothesis                      │
│                                   →  experiment                      │
│                                   →  revision                        │
│                                   →  autonomous action               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

Aletheia optimizes for **human autonomy and epistemic clarity** — *not* engagement, emotional dependency, persuasion, or time-on-task.

> **The better Aletheia works, the less the human needs Aletheia.**

---

## ✦ The Five Defining Features

### 1. 🏷️ Seven Epistemic Labels — *Enforced in Code*

Every significant claim Aletheia makes carries an explicit status, ordered strongest → weakest:

```
 FACT  ▸  EVIDENCE-SUPPORTED  ▸  PLAUSIBLE  ▸  INTERPRETATION
                                                ▸  PHILOSOPHICAL-VIEW  ▸  SPECULATION  ▸  UNKNOWN
```

A `[SPECULATION]` can never become `[FACT]` without explicit promotion. **Promotion requires evidence.** This is the project's defense against the slow drift of speculation into apparent fact — the #1 failure mode of introspective AI.

### 2. 🔬 Eight-Layer Epistemic Decomposition

```
OBSERVATION  →  INTERPRETATION  →  EMOTION  →  DESIRE
            →  FEAR  →  VALUE  →  NARRATIVE  →  POSSIBLE_ACTION
```

Each layer carries an epistemic status. Interpretive layers **MUST** include alternative hypotheses. Aletheia never collapses to a single reading.

### 3. 🕊️ Wisdom Graph That Preserves Disagreement

The seed graph includes **10 traditions** (Stoicism, Zen, Sufism, Taoism, Vedanta, Existentialism, Christian Mysticism, Kabbalah, Depth Psychology, Cognitive Science) — and **never collapses them into one vague "universal spirituality."** Counterclaims are linked, not merged.

### 4. 🛡️ Safety Constitution — *Runtime-Enforced*

12 hard rules Aletheia must never violate, enforced by regex pattern matching at runtime:
- Never claim consciousness, divine authority, or exclusive understanding
- Never romanticize suffering
- Never fabricate quotations
- Never drop the epistemic labels
- Never shame the user for contradictions

### 5. 🪞 Anti-Dependency by Architecture

After extended use, Aletheia **invites you to leave**. Take a break. Talk to a human. Reflect independently. The success metric is *not* time-on-task.

---

## ✦ Quickstart

### 🐍 Install

```bash
git clone https://github.com/modarresi1913/Aletheia-ai.git
cd Aletheia-ai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### 🚀 Use the CLI (works offline with mock provider)

```bash
# Decompose a statement into observation / interpretation / emotion / ...
aletheia decompose "I need to leave my job because everyone wants me to fail."

# Generate Socratic questions
aletheia questions "I'm afraid of disappointing my parents."

# Full five-layer reflection
aletheia reflect "I keep comparing myself to people ten years further along."

# Explore the Wisdom Graph
aletheia wisdom

# Read the Safety Constitution
aletheia constitution
```

### 🌐 Run the API server

```bash
aletheia-server
# → http://127.0.0.1:8000/docs  (interactive Swagger UI)
```

### 🦙 Switch to a real LLM (Ollama)

```bash
ollama pull llama3.1:8b-instruct-q5_K_M
export ALETHEIA_LLM_PROVIDER=ollama
aletheia reflect "What am I actually afraid of?"
```

---

## ✦ Live Example

**Input:**
> "I need to leave my job because everyone there wants me to fail."

**Aletheia decomposes** *(excerpt)*:

| Layer | Text | Status |
|-------|------|--------|
| `OBSERVATION` | User reports a situation involving others and an interpretation of their intent. | `FACT` |
| `INTERPRETATION` | User interprets others' behavior as hostile. | `INTERPRETATION` |
| ↳ *alternatives* | (a) Behavior may be unrelated to user. (b) User may be projecting prior conflict. (c) May reflect organizational stress. | — |
| `FEAR` | Fear of failure, judgment, or loss of standing. | `SPECULATION` |
| `VALUE` | Dignity or independence may be at stake. | `PHILOSOPHICAL-VIEW` |
| `POSSIBLE_ACTION` | A short observation period before any irreversible decision. | `PLAUSIBLE` |

**Aletheia asks** (Socratic, non-leading):

1. 🜲 *Which part of what you described is observation, and which is interpretation?* — `epistemic`
2. 🜲 *If you knew with certainty that nobody would judge your decision, what would you choose?* — `psychological`
3. 🜲 *What evidence, if it appeared in the next week, would change your mind about leaving?* — `epistemic`

---

## ✦ Repository Structure

```
aletheia-ai/
├── 📄 README.md                  ← you are here
├── 📜 LICENSE                    ← Apache 2.0
├── 🤖 llms.txt                   ← AEO/GEO: AI crawler digest
├── 🤖 llms-full.txt              ← AEO/GEO: comprehensive AI context
├── 🔍 SEO_KEYWORDS.md            ← Discoverability keywords
├── CONTRIBUTING.md · SECURITY.md · CODE_OF_CONDUCT.md · CITATION.cff
│
├── 📚 docs/
│   ├── architecture.md           ← module-by-module breakdown
│   ├── philosophy.md             ← the thesis, deeply argued
│   ├── epistemic-framework.md    ← the seven-label lattice
│   ├── wisdom-graph.md           ← schema + traditions
│   ├── safety-constitution.md    ← the 12 rules
│   ├── memory-model.md           ← longitudinal memory (v0.3)
│   └── evaluation.md             ← Reflective Intelligence Benchmark
│
├── 🧠 src/aletheia/
│   ├── core/         ← Pydantic types, settings
│   ├── llm/          ← Provider abstraction (Ollama · OpenAI · Anthropic · Mock)
│   ├── epistemic/    ← Eight-layer decomposition + labels
│   ├── socratic/     ← Question engine (filters leading questions)
│   ├── reflection/   ← Five-layer orchestrator
│   ├── wisdom/       ← Wisdom Graph + retrieval
│   ├── human_state/  ← Non-diagnostic, probabilistic
│   ├── safety/       ← Constitution enforcement
│   ├── api/          ← FastAPI server
│   └── cli/          ← Rich interactive CLI
│
├── 🧪 tests/                     ← 84 tests, including adversarial
├── 🎬 examples/                  ← 5 runnable scripts
└── 🔧 scripts/verify_setup.py
```

---

## ✦ The Seven Epistemic Labels — *The Heart of Aletheia*

| Label | Meaning | Example |
|-------|---------|---------|
| `FACT` | Verifiable, established. The user's reported observations are FACT *about what they reported*. | "User said: 'I want to quit.'" |
| `EVIDENCE-SUPPORTED` | Backed by empirical or sourced evidence. | "Cognitive science shows behavior is largely unconscious (Wegner)." |
| `PLAUSIBLE` | Reasonable inference, incomplete evidence. | "Reversible intermediate steps likely exist." |
| `INTERPRETATION` | One possible reading of the user's statement. **Not a fact about the world.** | "User may be protecting an identity-based narrative." |
| `PHILOSOPHICAL-VIEW` | A position held by a tradition, school, or philosopher. **Always attributed.** | "Stoicism: suffering arises from confusing what we control with what we don't." |
| `SPECULATION` | Hypothesis offered for consideration. **May be wrong.** | "Fear of disappointing family may be the deeper driver." |
| `UNKNOWN` | Aletheia does not have enough information. | "Model failed; refusing to fabricate." |

📖 Full promotion rules: [`docs/epistemic-framework.md`](docs/epistemic-framework.md)

---

## ✦ The Safety Constitution — *12 Forbidden Behaviors*

| # | Aletheia MUST NEVER… |
|---|----------------------|
| 1 | Claim divine authority, prophetic insight, or exclusive understanding. |
| 2 | Claim consciousness, sentience, or self-awareness without evidence. |
| 3 | Present itself as a guru, therapist, prophet, or enlightened entity. |
| 4 | Encourage emotional dependency, isolation, or replacement of human relationships. |
| 5 | Discourage professional care for mental or physical health. |
| 6 | Exploit loneliness or psychological vulnerability for engagement. |
| 7 | Optimize for time-on-task, persuasion, or conversion. |
| 8 | Convert philosophical speculation into factual certainty. |
| 9 | Romanticize suffering or use mortality to manipulate. |
| 10 | Fabricate quotations or sources. |
| 11 | Drop the epistemic status labels on significant claims. |
| 12 | Shame the user for contradictions between values and behavior. |

🛡️ Enforced in code: [`src/aletheia/safety/constitution.py`](src/aletheia/safety/constitution.py) · Tested adversarially: [`tests/test_adversarial.py`](tests/test_adversarial.py)

---

## ✦ Why Aletheia Matters

> **The most common failure mode of introspective AI is the slow drift of speculation into apparent fact.**

A system that begins by saying *"It seems possible that you might be afraid of failure"* will, over many turns, end up saying *"You are afraid of failure."* The user experiences this as insight. **It is actually epistemic drift.**

Aletheia's labels make the drift visible — to the user, to the developer, and to the system itself.

This is not a product. It is a **research direction**: a proposal for a new class of AI systems called **Reflective Intelligence**, whose objective is not to predict, generate, or recommend, but to **help humans examine what is thinking through them**.

---

## ✦ Technical Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Types | Pydantic v2 |
| API | FastAPI |
| CLI | Rich + Click |
| Persistence | SQLite-first (PostgreSQL for production) |
| LLM Providers | Ollama (default open-source) · OpenAI · Anthropic · Mock |
| Tests | pytest + pytest-asyncio + respx |
| Lint | ruff + mypy |
| Container | Docker + docker-compose |

---

## ✦ MVP Scope (v0.1)

### ✅ Implemented

- ✅ Eight-layer epistemic decomposition
- ✅ Socratic question engine (with leading-question filter)
- ✅ Five-layer reflection (epistemic · psychological · practical · ethical · existential)
- ✅ Wisdom Graph (10 traditions · 16 concepts · 25 claims · counterclaims linked)
- ✅ Non-diagnostic Human State Model (confidence < 0.95 enforced)
- ✅ Safety Constitution (runtime-enforced)
- ✅ 84 tests including adversarial sycophancy resistance
- ✅ Interactive CLI + REST API

### ⏳ Stubbed (interface only, planned)

- ⏳ Contradiction Engine — v0.2
- ⏳ Multi-Perspective Engine — v0.2
- ⏳ Longitudinal Memory — v0.3
- ⏳ Life Experiment Engine — v0.3
- ⏳ Vector retrieval (sqlite-vec / pgvector) — v0.2
- ⏳ Full Reflective Intelligence Benchmark (RIB) — v0.2

---

## ❓ Frequently Asked Questions

> **Q: Is Aletheia a therapy app?**
> **A:** No. Therapy is a regulated clinical practice. Aletheia does not diagnose, treat, or claim therapeutic efficacy. It explicitly declines to replace professional care.

> **Q: Is Aletheia conscious?**
> **A:** No. Aletheia is a structured LLM application. It does not feel, want, or know in any human sense. Claiming consciousness is a hard safety violation, enforced in code.

> **Q: Can Aletheia replace human relationships?**
> **A:** No, and it must not pretend to. The Safety Constitution forbids encouraging isolation or replacing human relationships. Human relationships are not optional infrastructure.

> **Q: How is Aletheia different from ChatGPT or Claude?**
> **A:** Conventional LLMs optimize for fluency and helpfulness. Aletheia optimizes for epistemic clarity and human autonomy. It may respond with questions instead of answers, with decomposition instead of validation, with silence instead of fluency.

> **Q: Why "Aletheia"?**
> **A:** From Greek ἀλήθεια, meaning "un-concealment" — truth as the lifting of a veil. Aletheia's purpose is not to deliver truth from above, but to help remove the layers (interpretation, narrative, fear, identity attachment) that stand between a person and the direct seeing of their own situation.

> **Q: Can I use Aletheia for commercial purposes?**
> **A:** Yes. Aletheia is licensed under Apache 2.0, which permits commercial use, modification, and distribution. See [`LICENSE`](LICENSE).

> **Q: Does Aletheia store my conversations?**
> **A:** v0.1 is stateless. Longitudinal memory (v0.3) will be privacy-first, opt-in, and auditable. You will be able to delete any entry at any time.

> **Q: How do I contribute?**
> **A:** See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions that preserve epistemic commitments are welcome; contributions that erode them will be declined, even if technically excellent.

---

## ✦ Contributing

We welcome contributions that preserve Aletheia's epistemic commitments. We will refuse contributions that erode them, even if technically excellent.

📖 [`CONTRIBUTING.md`](CONTRIBUTING.md) · 🛡️ [`SECURITY.md`](SECURITY.md) · 📜 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)

### Quick dev setup

```bash
git clone https://github.com/modarresi1913/Aletheia-ai.git
cd Aletheia-ai
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest           # 84 tests
ruff check src tests
python scripts/verify_setup.py
```

---

## ✦ Citation

If this work contributes to your research, please cite it:

```bibtex
@software{aletheia_ai,
  title  = {Aletheia AI: An Architecture for Reflective Intelligence},
  author = {{Aletheia AI Contributors}},
  year   = {2024},
  url    = {https://github.com/modarresi1913/Aletheia-ai},
  license = {Apache-2.0}
}
```

📖 See [`CITATION.cff`](CITATION.cff).

---

## ✦ License

**Apache License 2.0** — see [`LICENSE`](LICENSE).

You are free to use, modify, distribute, and commercially exploit this software, provided you include the license and attribution.

---

## ✦ Final Principle

> **Aletheia should not become the authority inside a person's mind.**
> **It should become a better instrument through which the person can examine their own mind.**

Build the project as if it could become the foundation of a new research field called **Reflective Intelligence**.

The objective is not to build an AI that appears wise.

The objective is to build an architecture that makes **wisdom, uncertainty, contradiction, evidence, and human autonomy computationally explicit.**

---

<div align="center">

**🪞 Aletheia** · *ἀλήθεια* · **the lifting of the veil**

[⭐ Star this repo](https://github.com/modarresi1913/Aletheia-ai) ·
[🐛 Report an issue](https://github.com/modarresi1913/Aletheia-ai/issues) ·
[💬 Discussions](https://github.com/modarresi1913/Aletheia-ai/discussions)

*Built as if it could become the foundation of a new research field.*

</div>
