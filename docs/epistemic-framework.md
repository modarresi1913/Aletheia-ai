# Epistemic Framework

## 1. The seven status labels

Aletheia's defining technical feature is that every significant claim carries an explicit epistemic status. The labels are ordered from strongest to weakest:

| Rank | Label | Meaning |
|------|-------|---------|
| 7 | `FACT` | Established, verifiable. The user's own reported observable events are also `FACT` *about what they reported*, not about underlying reality. |
| 6 | `EVIDENCE-SUPPORTED` | Backed by empirical or textual evidence with sources. |
| 5 | `PLAUSIBLE` | Reasonable inference, but evidence is incomplete or indirect. |
| 4 | `INTERPRETATION` | One possible reading of the user's statement. Not a fact about the world. |
| 3 | `PHILOSOPHICAL-VIEW` | A position held by a tradition, school, or philosopher. Always attributed. |
| 2 | `SPECULATION` | Hypothesis offered for consideration. May be wrong. |
| 1 | `UNKNOWN` | Aletheia does not have enough information. |

## 2. Promotion rules

A claim may move from a weaker to a stronger status only when explicit evidence justifies it. Demotion (stronger → weaker) is allowed when counterevidence appears.

```
SPECULATION → PLAUSIBLE → EVIDENCE-SUPPORTED → FACT
   ↑                                                ↑
   └── counterevidence may demote at any time ──────┘
```

`INTERPRETATION` and `PHILOSOPHICAL-VIEW` are lateral categories, not on the same ladder:

- `INTERPRETATION` describes *the user's statement*, not the world.
- `PHILOSOPHICAL-VIEW` describes *a tradition's position*, not the world.

Both may be promoted to `EVIDENCE-SUPPORTED` only when independent empirical evidence appears.

## 3. The eight-layer decomposition

User statements are decomposed into an eight-layer chain:

```
OBSERVATION       — what observable events occurred (per the user's report)
   ↓
INTERPRETATION    — what the user concludes those events mean
   ↓
EMOTION           — what emotions are present or implied
   ↓
DESIRE            — what the user may want
   ↓
FEAR              — what the user may be afraid of
   ↓
VALUE             — what underlying value may be at stake
   ↓
NARRATIVE         — what story the user is telling themselves
   ↓
POSSIBLE_ACTION   — what concrete actions are available
```

Rules:

1. Each layer carries an epistemic status.
2. The interpretive layers (`INTERPRETATION`, `DESIRE`, `FEAR`, `VALUE`, `NARRATIVE`) MUST include at least one alternative hypothesis. Aletheia never collapses to a single reading.
3. The `OBSERVATION` layer's status is `FACT` *about the user's report*, not about the underlying reality. Reported observations are not independently verified.
4. The decomposition never validates the user's conclusion. It separates the conclusion from the evidence.
5. If the LLM fails, the decomposition falls back to an `UNKNOWN` decomposition rather than fabricating one.

## 4. The five reflection layers

Each statement may be reflected on through up to five layers. Not all are invoked on every turn.

| Layer | Question |
|-------|----------|
| `epistemic` | What do we actually know? |
| `psychological` | What emotions, assumptions, cognitive patterns may be involved? |
| `practical` | What is happening in the real world? What actions are available? |
| `ethical` | Who else may be affected? |
| `existential` | What does this reveal about meaning, identity, mortality, freedom, or purpose? |

Each layer's output must contain at least one epistemic label inline (`[FACT]`, `[PLAUSIBLE]`, etc.) and at least one alternative interpretation marked `[SPECULATION]`.

## 5. Sourcing rules

1. Every quoted `WisdomClaim` must have a `SourceCitation` with at least the `tradition` field set.
2. When `work` is set, `locator` (page, chapter, verse) is strongly recommended.
3. Fabricated quotations are forbidden. If a quotation cannot be verified, Aletheia paraphrases and labels the claim `[PHILOSOPHICAL-VIEW]` attributed to the tradition.
4. The seed graph (`src/aletheia/data/seed.jsonl`) contains only real, verifiable sources.

## 6. Probabilistic language

When estimating the user's state or motivations, Aletheia uses probabilistic language:

- "One possibility is..."
- "A pattern worth examining may be..."
- "The conversation provides weak/moderate evidence for..."
- "This is an interpretation, not a conclusion."

The Human State Model is forbidden from reaching confidence ≥ 0.95. This is enforced in the type system (`HumanStateEstimate._enforce_uncertainty`).

## 7. What the labels prevent

The label system is the project's defense against the most common failure mode of introspective AI: **the slow drift of speculation into apparent fact**.

Without enforced labels, a system that begins by saying "It seems possible that you might be afraid of failure" will, over many turns and many model updates, end up saying "You are afraid of failure." The user experiences this as insight. It is actually epistemic drift.

The labels make the drift visible — to the user, to the developer, and to the system itself. A claim labeled `[SPECULATION]` cannot be re-used as `[FACT]` without explicit promotion, and promotion requires evidence.

## 8. Self-revision

Every long-term hypothesis in Aletheia carries a lifecycle status (planned for v0.3):

- `active` — currently held
- `weakened` — counterevidence has appeared
- `rejected` — has been disproven
- `unresolved` — evidence is mixed
- `superseded` — replaced by a better hypothesis

Aletheia should be able to say: *"My earlier interpretation appears incomplete."* This is a fundamental architectural principle, not a polite phrase.
