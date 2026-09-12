"""Tests for the Life Experiment Engine (v0.3)."""
from __future__ import annotations

from pathlib import Path

import pytest

from aletheia.core.types import EpistemicStatus
from aletheia.experiments.engine import ExperimentEngine
from aletheia.experiments.types import ExperimentOutcome, LifeExperiment
from aletheia.memory.store import LongitudinalMemory


@pytest.fixture
def engine(tmp_path: Path) -> ExperimentEngine:
    memory = LongitudinalMemory(db_path=tmp_path / "test_exp.db")
    return ExperimentEngine(memory=memory)


class TestLifeExperiment:
    def test_construct(self) -> None:
        e = LifeExperiment(
            id="exp_1",
            title="Seven-day observation",
            hypothesis="Observation may reveal a pattern.",
            protocol=["Write daily.", "Re-read after 7 days."],
        )
        assert e.id == "exp_1"
        assert e.status == "proposed"
        assert e.reversible is True
        assert e.duration_days == 7
        assert e.epistemic_status == EpistemicStatus.SPECULATION

    def test_start(self) -> None:
        e = LifeExperiment(id="e1", title="T", hypothesis="H", protocol=[])
        e.start()
        assert e.status == "active"
        assert e.start_date is not None

    def test_start_fails_if_already_started(self) -> None:
        e = LifeExperiment(id="e1", title="T", hypothesis="H", protocol=[])
        e.start()
        with pytest.raises(ValueError):
            e.start()

    def test_complete(self) -> None:
        e = LifeExperiment(id="e1", title="T", hypothesis="H", protocol=[])
        e.start()
        outcome = ExperimentOutcome(
            outcome="hypothesis_supported",
            summary="Pattern confirmed.",
            evidence_collected=["Day 3 entry"],
        )
        e.complete(outcome)
        assert e.status == "completed"
        assert e.outcome is not None
        assert e.outcome.outcome == "hypothesis_supported"

    def test_abandon(self) -> None:
        e = LifeExperiment(id="e1", title="T", hypothesis="H", protocol=[])
        e.start()
        e.abandon("User chose not to continue")
        assert e.status == "abandoned"
        assert e.outcome is not None
        assert e.outcome.outcome == "abandoned"


class TestExperimentEngine:
    def test_propose_returns_experiments(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose("I'm afraid of failing my career.")
        assert isinstance(proposals, list)
        assert len(proposals) >= 1
        for p in proposals:
            assert isinstance(p, LifeExperiment)
            assert p.status == "proposed"
            assert p.reversible is True
            assert len(p.protocol) >= 1

    def test_propose_with_fear_signals(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose(
            "I'm scared.",
            signals={"fear"},
        )
        assert len(proposals) >= 1
        # Fear-removal test should be one of the proposals when fear signal is present
        titles = [p.title.lower() for p in proposals]
        assert any("fear" in t for t in titles) or any("observation" in t for t in titles)

    def test_propose_with_internal_conflict(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose(
            "Part of me wants to leave, part of me wants to stay.",
            signals={"internal_conflict", "uncertainty"},
        )
        assert len(proposals) >= 1
        # Two-futures experiment should be relevant
        titles = [p.title.lower() for p in proposals]
        assert any("future" in t or "observation" in t for t in titles)

    def test_propose_always_returns_at_least_one(self, engine: ExperimentEngine) -> None:
        """Even with no matching signals, the observation experiment is returned."""
        proposals = engine.propose(
            "Random statement with no clear signals.",
            signals=set(),
        )
        assert len(proposals) >= 1

    def test_propose_max_proposals(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose(
            "I'm afraid, uncertain, ashamed, and torn.",
            signals={"fear", "uncertainty", "shame", "internal_conflict"},
            max_proposals=2,
        )
        assert len(proposals) <= 2

    def test_start_complete_lifecycle(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose("I'm afraid.")
        exp_id = proposals[0].id
        started = engine.start(exp_id)
        assert started.status == "active"
        outcome = ExperimentOutcome(
            outcome="hypothesis_weakened",
            summary="The fear did not diminish.",
        )
        completed = engine.complete(exp_id, outcome)
        assert completed.status == "completed"
        assert completed.outcome is not None

    def test_complete_updates_linked_hypothesis(self, engine: ExperimentEngine) -> None:
        # Create a hypothesis in memory
        h = engine.memory.add(
            kind="hypothesis",
            text="User fears failure.",
            user_id="alice",
        )
        # Create an experiment linked to the hypothesis
        proposals = engine.propose("I'm afraid.", user_id="alice")
        exp = proposals[0]
        exp.hypothesis_entry_id = h.id
        engine._experiments[exp.id] = exp
        # Start and complete with supportive outcome
        engine.start(exp.id)
        outcome = ExperimentOutcome(
            outcome="hypothesis_supported",
            summary="The fear was confirmed by observation.",
        )
        engine.complete(exp.id, outcome)
        # Check the hypothesis was strengthened
        updated = engine.memory.get(h.id)
        assert updated is not None
        assert len(updated.evidence) >= 1

    def test_complete_with_rejection_marks_hypothesis_rejected(self, engine: ExperimentEngine) -> None:
        h = engine.memory.add(
            kind="hypothesis",
            text="User fears failure.",
            user_id="alice",
        )
        proposals = engine.propose("I'm afraid.", user_id="alice")
        exp = proposals[0]
        exp.hypothesis_entry_id = h.id
        engine._experiments[exp.id] = exp
        engine.start(exp.id)
        outcome = ExperimentOutcome(
            outcome="hypothesis_rejected",
            summary="The fear hypothesis was not supported.",
        )
        engine.complete(exp.id, outcome)
        updated = engine.memory.get(h.id)
        from aletheia.core.types import HypothesisStatus
        assert updated is not None
        assert updated.hypothesis_status == HypothesisStatus.REJECTED

    def test_render(self, engine: ExperimentEngine) -> None:
        proposals = engine.propose("I'm afraid.")
        text = engine.render(proposals[0])
        assert "EXPERIMENT" in text
        assert "hypothesis" in text.lower()
        assert "PROTOCOL" in text
        assert "SUCCESS CRITERIA" in text
        assert "SPECULATION" in text  # epistemic label
