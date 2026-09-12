# Memory Model

> **Memory ≠ truth.**

## Status

This document describes the **planned** memory model for Aletheia v0.3. The MVP (v0.1) does not implement longitudinal memory; the `memory/` module is a typed stub with the interface sketched here.

## Principles

1. **Memory entries are revisable hypotheses, not facts about the user.** Every entry carries an `epistemic_status` and a `hypothesis_status` that can change over time.
2. **Privacy-first.** Only signal-bearing entries are stored. The system does not accumulate transcripts.
3. **Explicit revisability.** Any stored hypothesis can be marked `weakened`, `rejected`, or `superseded` when counterevidence appears.
4. **The user can audit and delete.** Memory is not opaque.

## What is stored

| Kind | Example | Notes |
|------|---------|-------|
| `declared_value` | "The user has repeatedly described freedom as highly important." | What the user says matters to them |
| `decision` | "On 2024-03-15, the user chose to start a seven-day observation period." | Concrete commitments |
| `experiment` | "Seven-day observation: completed; pattern of avoidance noted." | Tracked experiments and outcomes |
| `hypothesis` | "Fear of disappointing family may be a stronger driver than stated career concerns." | Revisable interpretations |
| `pattern` | "Across 5 sessions, the user consistently raises comparison themes when discussing work." | Observed regularities |

## What is NOT stored

- Full transcripts
- Specific personal details not relevant to reflection
- Anything the user asks to be forgotten
- Sensitive health or relationship details beyond what reflection requires

## Hypothesis lifecycle

Every `MemoryEntry` of kind `hypothesis` carries a `hypothesis_status`:

```python
class HypothesisStatus(str, Enum):
    ACTIVE = "active"           # currently held
    WEAKENED = "weakened"       # counterevidence has appeared
    REJECTED = "rejected"       # has been disproven
    UNRESOLVED = "unresolved"   # evidence is mixed
    SUPERSEDED = "superseded"   # replaced by a better hypothesis
```

When Aletheia revises a hypothesis, the old entry is marked `SUPERSEDED` and a new entry is created with a back-reference. The history is preserved.

## Personal Reflection Report

Periodically (e.g. every 10 sessions, or on user request), the system produces a report:

```text
PERSONAL REFLECTION REPORT
────────────────────────────────────────
Recurring themes:
  - Comparison with peers (5 sessions)
  - Career-direction uncertainty (4 sessions)
  - Family expectations (3 sessions)

Unresolved questions:
  - Is the stated priority on freedom stable, or a reaction to current constraints?

Value/behavior tensions:
  - Declared value: freedom
    Recent decisions: prioritized security (3 of last 5)
    Interpretation: definition of freedom may have shifted, not necessarily inconsistency.

Hypotheses that gained evidence:
  - "Fear of disappointing family is a stronger driver than stated." (3 corroborating instances)

Hypotheses that lost evidence:
  - "Burnout is the primary cause." (user reports stable energy levels)

Completed experiments:
  - Seven-day observation: completed; no strong pattern visible.

Changes in perspective:
  - Earlier interpretation of "everyone wants me to fail" appears incomplete.
    Supervening hypothesis: organizational stress, not personal hostility.
```

The report explicitly distinguishes **memory** (what was stored) from **truth** (what is the case). A pattern in memory is a pattern in what Aletheia has heard, not a fact about the user.

## Storage (planned)

- **v0.3 (planned):** SQLite with semantic search via sqlite-vec.
- **v0.4+ (planned):** PostgreSQL with pgvector for production deployments.
- **Encryption at rest:** required for any deployment that stores user memory.

## Deletion

Users can request:
- Deletion of a specific entry by ID
- Deletion of all hypotheses about a specific topic
- Complete memory wipe

Deletion is irreversible. The system does not maintain soft-deleted copies.

## Privacy commitments

1. Memory is per-user. There is no cross-user learning from stored memory.
2. Memory is not used for advertising, marketing, or any commercial purpose.
3. Memory is not shared with third parties without explicit user consent.
4. The user can export their full memory at any time as JSON.
