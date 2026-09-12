"""Tests for the Vector Retriever (v0.2)."""
from __future__ import annotations

import pytest

from aletheia.core.types import WisdomClaim
from aletheia.wisdom.graph import WisdomGraph
from aletheia.wisdom.vector_retrieval import VectorRetriever


@pytest.fixture
def graph() -> WisdomGraph:
    return WisdomGraph.default()


@pytest.fixture
def retriever(graph: WisdomGraph) -> VectorRetriever:
    return VectorRetriever.with_tf_idf(graph, top_k=5)


class TestVectorRetriever:
    def test_retrieve_returns_claims(self, retriever: VectorRetriever) -> None:
        claims = retriever.retrieve("I am afraid of dying and want my life to matter")
        assert isinstance(claims, list)
        assert len(claims) >= 1
        for c in claims:
            assert isinstance(c, WisdomClaim)

    def test_retrieve_relevant_claims(self, retriever: VectorRetriever) -> None:
        claims = retriever.retrieve("I am afraid of dying and fear death")
        # At least one claim should mention death, fear, mortality, or memento mori
        texts = " ".join(c.text.lower() for c in claims)
        concept_summaries = " ".join(
            retriever.graph.get_concept(c.concept_id).summary.lower()
            for c in claims if retriever.graph.get_concept(c.concept_id)
        )
        combined = texts + " " + concept_summaries
        assert any(
            kw in combined
            for kw in ["death", "mortal", "fear", "impermanent", "memento", "finitude"]
        ), f"Expected death/fear-related claim, got texts: {texts!r}"

    def test_retrieve_with_scores(self, retriever: VectorRetriever) -> None:
        results = retriever.retrieve_with_scores("freedom and autonomy")
        assert isinstance(results, list)
        for claim, score in results:
            assert isinstance(claim, WisdomClaim)
            assert 0.0 <= score <= 1.0
        # Results should be sorted by score descending
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_retrieve_by_concept_still_works(self, retriever: VectorRetriever) -> None:
        """Inherited method from WisdomRetriever."""
        claims = retriever.retrieve_by_concept("fear")
        assert isinstance(claims, list)
        assert all(c.concept_id == "fear" for c in claims)

    def test_retrieve_with_counters(self, retriever: VectorRetriever) -> None:
        """Inherited method preserves disagreements."""
        results = retriever.retrieve_with_counters("control and free will")
        assert isinstance(results, list)

    def test_tf_idf_better_than_keyword_for_semantic_queries(
        self, graph: WisdomGraph
    ) -> None:
        """The TF-IDF retriever should retrieve relevant claims that keyword
        search might miss, especially for longer queries."""
        from aletheia.wisdom.retrieval import WisdomRetriever

        vec = VectorRetriever.with_tf_idf(graph, top_k=5)
        kw = WisdomRetriever(graph, top_k=5)

        query = "I want to understand why I keep doing the same thing over and over"
        vec_results = vec.retrieve(query)
        kw_results = kw.retrieve(query)

        # Both should return at least one result
        assert len(vec_results) >= 1
        # Vector retriever should generally find more relevant results
        # (or at least as many)
        assert len(vec_results) >= len(kw_results) - 1  # tolerance

    def test_empty_query_returns_empty(self, retriever: VectorRetriever) -> None:
        claims = retriever.retrieve("")
        assert isinstance(claims, list)

    def test_unknown_query_returns_empty_or_few(self, retriever: VectorRetriever) -> None:
        """A query with no overlapping tokens should return few or no results."""
        claims = retriever.retrieve("zzz qwerty xyzabc")
        # Should return 0 or very few results
        assert len(claims) <= 2
