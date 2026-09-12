"""Wisdom Graph data model and persistence.

The Wisdom Graph is the knowledge representation layer of Aletheia. It contains:

- `Tradition`   — a philosophical, spiritual, or scientific tradition
- `Concept`     — a node (ego, desire, attachment, freedom, ...)
- `WisdomClaim` — a claim made by a tradition about a concept, with citation

The graph preserves disagreements: a `WisdomClaim` may carry `counterclaims`
pointing to opposing claims from other traditions. Aletheia never collapses
different philosophical traditions into one vague "universal spirituality."
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import structlog
from pydantic import ValidationError

from ..core.types import Concept, Tradition, WisdomClaim

log = structlog.get_logger(__name__)


class WisdomGraph:
    """In-memory Wisdom Graph.

    Persistence: serializes to JSONL. SQLite + pgvector support is planned
    but not in the MVP scope (see `docs/architecture.md`).
    """

    def __init__(
        self,
        traditions: list[Tradition] | None = None,
        concepts: list[Concept] | None = None,
        claims: list[WisdomClaim] | None = None,
    ) -> None:
        self.traditions: dict[str, Tradition] = {t.id: t for t in (traditions or [])}
        self.concepts: dict[str, Concept] = {c.id: c for c in (concepts or [])}
        self.claims: dict[str, WisdomClaim] = {c.id: c for c in (claims or [])}

    # ── factories ─────────────────────────────────────────────

    @classmethod
    def default(cls) -> WisdomGraph:
        """Load the bundled seed graph."""
        return cls.from_seed()

    @classmethod
    def from_seed(cls) -> WisdomGraph:
        """Load the seed graph bundled with the package."""
        seed_path = Path(__file__).resolve().parent.parent / "data" / "seed.jsonl"
        if not seed_path.exists():
            log.warning("wisdom.seed.missing", path=str(seed_path))
            return cls()
        return cls.from_jsonl(seed_path)

    @classmethod
    def from_jsonl(cls, path: Path | str) -> WisdomGraph:
        """Load a Wisdom Graph from a JSONL file.

        Each line is one of:
            {"type": "tradition", "data": {...}}
            {"type": "concept",   "data": {...}}
            {"type": "claim",     "data": {...}}
        """
        path = Path(path)
        traditions: list[Tradition] = []
        concepts: list[Concept] = []
        claims: list[WisdomClaim] = []

        with path.open("r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    log.warning("wisdom.seed.bad_line", line=lineno, error=str(e))
                    continue
                kind = obj.get("type")
                data = obj.get("data", {})
                try:
                    if kind == "tradition":
                        traditions.append(Tradition(**data))
                    elif kind == "concept":
                        concepts.append(Concept(**data))
                    elif kind == "claim":
                        claims.append(WisdomClaim(**data))
                    else:
                        log.warning("wisdom.seed.unknown_type", line=lineno, type=kind)
                except ValidationError as e:
                    log.warning("wisdom.seed.validation", line=lineno, error=e.errors())

        log.info(
            "wisdom.seed.loaded",
            traditions=len(traditions),
            concepts=len(concepts),
            claims=len(claims),
            path=str(path),
        )
        return cls(traditions=traditions, concepts=concepts, claims=claims)

    # ── accessors ─────────────────────────────────────────────

    def get_concept(self, concept_id: str) -> Concept | None:
        return self.concepts.get(concept_id)

    def get_claim(self, claim_id: str) -> WisdomClaim | None:
        return self.claims.get(claim_id)

    def claims_for_concept(self, concept_id: str) -> list[WisdomClaim]:
        return [c for c in self.claims.values() if c.concept_id == concept_id]

    def claims_by_tradition(self, tradition_id: str) -> list[WisdomClaim]:
        return [c for c in self.claims.values() if c.tradition == tradition_id]

    def counterclaims(self, claim_id: str) -> list[WisdomClaim]:
        claim = self.claims.get(claim_id)
        if not claim:
            return []
        return [self.claims[c] for c in claim.counterclaims if c in self.claims]

    def concepts_by_tradition(self, tradition_id: str) -> list[Concept]:
        return [c for c in self.concepts.values() if tradition_id in c.traditions]

    def all_concepts(self) -> Iterable[Concept]:
        return self.concepts.values()

    def all_claims(self) -> Iterable[WisdomClaim]:
        return self.claims.values()

    # ── mutation ──────────────────────────────────────────────

    def add_tradition(self, t: Tradition) -> None:
        self.traditions[t.id] = t

    def add_concept(self, c: Concept) -> None:
        self.concepts[c.id] = c

    def add_claim(self, c: WisdomClaim) -> None:
        if c.concept_id not in self.concepts:
            raise ValueError(f"Cannot add claim: unknown concept_id={c.concept_id!r}")
        self.claims[c.id] = c

    # ── introspection ─────────────────────────────────────────

    def stats(self) -> dict[str, int]:
        return {
            "traditions": len(self.traditions),
            "concepts": len(self.concepts),
            "claims": len(self.claims),
        }

    def __repr__(self) -> str:
        s = self.stats()
        return f"WisdomGraph(traditions={s['traditions']}, concepts={s['concepts']}, claims={s['claims']})"

    def render_summary(self) -> str:
        lines = ["Wisdom Graph", "────────────────────────────────"]
        for tid, t in self.traditions.items():
            count = len(self.claims_by_tradition(tid))
            lines.append(f"  [{tid}] {t.name} — {count} claim(s)")
        lines.append("")
        lines.append("Concepts:")
        for cid, c in self.concepts.items():
            n_claims = len(self.claims_for_concept(cid))
            lines.append(f"  {c.label} ({n_claims} claim(s)) [{c.epistemic_status.value}]")
        return "\n".join(lines)
