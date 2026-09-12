"""Wisdom Graph retrieval.

MVP retrieval is intentionally simple: keyword + concept matching over the
in-memory graph. Vector-based retrieval (sqlite-vec / pgvector) is a planned
extension and the interface here is designed to swap in cleanly.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from ..core.types import WisdomClaim
from .graph import WisdomGraph


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) > 2}


class WisdomRetriever:
    """Keyword + concept-matching retriever for the Wisdom Graph."""

    def __init__(self, graph: WisdomGraph, top_k: int = 3) -> None:
        self.graph = graph
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float = 0.05,
    ) -> list[WisdomClaim]:
        """Return up to `top_k` claims most relevant to `query`."""
        k = top_k or self.top_k
        q_tokens = _tokenize(query)

        scored: list[tuple[float, WisdomClaim]] = []
        for claim in self.graph.all_claims():
            concept = self.graph.get_concept(claim.concept_id)
            concept_label = concept.label if concept else ""
            concept_summary = concept.summary if concept else ""
            tokens = _tokenize(
                f"{claim.text} {concept_label} {concept_summary} {claim.tradition}"
            )
            if not tokens or not q_tokens:
                continue
            intersection = q_tokens & tokens
            if not intersection:
                continue
            # Score = overlap coefficient (intersection / min(|q|, |tokens|)).
            # This is more permissive than Jaccard and better for short queries.
            denom = min(len(q_tokens), len(tokens))
            score = len(intersection) / denom
            if score >= min_score:
                scored.append((score, claim))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]

    def retrieve_by_concept(self, concept_id: str) -> list[WisdomClaim]:
        return self.graph.claims_for_concept(concept_id)

    def retrieve_with_counters(self, query: str, top_k: int | None = None) -> list[WisdomClaim]:
        """Retrieve claims AND their counterclaims (preserves disagreement)."""
        primary = self.retrieve(query, top_k=top_k)
        out: list[WisdomClaim] = []
        seen: set[str] = set()
        for c in primary:
            if c.id not in seen:
                out.append(c)
                seen.add(c.id)
            for cc in self.graph.counterclaims(c.id):
                if cc.id not in seen:
                    out.append(cc)
                    seen.add(cc.id)
        return out

    def all_for_tradition(self, tradition_id: str) -> Iterable[WisdomClaim]:
        return self.graph.claims_by_tradition(tradition_id)
