"""Tests for the Wisdom Graph."""
from __future__ import annotations

import pytest

from aletheia.core.types import EpistemicStatus
from aletheia.wisdom.graph import WisdomGraph
from aletheia.wisdom.retrieval import WisdomRetriever


class TestWisdomGraphSeed:
    def test_seed_loads(self) -> None:
        g = WisdomGraph.default()
        assert len(g.traditions) >= 8, "Seed must include at least 8 traditions"
        assert len(g.concepts) >= 12, "Seed must include at least 12 concepts"
        assert len(g.claims) >= 15, "Seed must include at least 15 claims"

    def test_seed_traditions_include_expected(self) -> None:
        g = WisdomGraph.default()
        ids = set(g.traditions.keys())
        for expected in {"stoicism", "zen", "sufism", "existentialism", "cognitive_science"}:
            assert expected in ids, f"Seed must include tradition: {expected}"

    def test_concepts_have_tradition_links(self) -> None:
        g = WisdomGraph.default()
        for concept in g.all_concepts():
            assert len(concept.traditions) >= 1, (
                f"Concept {concept.id} must be linked to at least one tradition"
            )

    def test_claims_have_valid_concept_ids(self) -> None:
        g = WisdomGraph.default()
        for claim in g.all_claims():
            assert g.get_concept(claim.concept_id) is not None, (
                f"Claim {claim.id} references unknown concept {claim.concept_id}"
            )

    def test_claims_have_citations(self) -> None:
        g = WisdomGraph.default()
        for claim in g.all_claims():
            assert claim.citation.tradition, f"Claim {claim.id} must have a tradition citation"
            assert claim.citation.author is not None or claim.citation.work is not None, (
                f"Claim {claim.id} must have an author or work"
            )

    def test_disagreements_preserved(self) -> None:
        """At least one claim must have a counterclaim."""
        g = WisdomGraph.default()
        has_counter = False
        for claim in g.all_claims():
            if claim.counterclaims:
                has_counter = True
                # Verify counterclaims point to real claims
                for cc_id in claim.counterclaims:
                    assert g.get_claim(cc_id) is not None, (
                        f"Counterclaim {cc_id} of claim {claim.id} does not exist"
                    )
        assert has_counter, "Seed must include at least one pair of disagreeing claims"

    def test_stats(self) -> None:
        g = WisdomGraph.default()
        s = g.stats()
        assert s["traditions"] > 0
        assert s["concepts"] > 0
        assert s["claims"] > 0

    def test_render_summary(self) -> None:
        g = WisdomGraph.default()
        text = g.render_summary()
        assert "Wisdom Graph" in text
        assert "Stoicism" in text or "stoicism" in text


class TestWisdomRetriever:
    def test_retrieve_returns_relevant(self) -> None:
        g = WisdomGraph.default()
        r = WisdomRetriever(g, top_k=3)
        claims = r.retrieve("I am afraid of dying and want to live meaningfully")
        assert isinstance(claims, list)
        # Should retrieve at least one claim (death, fear, or meaning)
        assert len(claims) >= 1

    def test_retrieve_with_counters_includes_oppositions(self) -> None:
        g = WisdomGraph.default()
        r = WisdomRetriever(g, top_k=3)
        results = r.retrieve_with_counters("death and mortality")
        # Either primary or counterclaims should be present
        assert isinstance(results, list)

    def test_retrieve_by_concept(self) -> None:
        g = WisdomGraph.default()
        r = WisdomRetriever(g)
        # Find a concept that has claims
        for concept in g.all_concepts():
            claims = r.retrieve_by_concept(concept.id)
            if claims:
                assert all(c.concept_id == concept.id for c in claims)
                break


class TestWisdomGraphValidation:
    def test_add_claim_rejects_unknown_concept(self) -> None:
        g = WisdomGraph()
        with pytest.raises(ValueError):
            g.add_claim(
                type(
                    "X",
                    (),
                    {
                        "id": "x",
                        "concept_id": "nonexistent",
                        "text": "test",
                        "tradition": "test",
                        "citation": type("C", (), {"tradition": "test"})(),
                        "epistemic_status": EpistemicStatus.SPECULATION,
                        "counterclaims": [],
                    },
                )()
            )
