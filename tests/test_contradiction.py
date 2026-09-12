"""Tests for the Contradiction Engine (v0.2)."""
from __future__ import annotations

from pathlib import Path

import pytest

from aletheia.contradiction.detector import ContradictionDetector
from aletheia.contradiction.engine import ContradictionEngine
from aletheia.contradiction.types import Contradiction, ContradictionDetection
from aletheia.core.types import EpistemicStatus
from aletheia.memory.store import LongitudinalMemory


@pytest.fixture
def memory(tmp_path: Path) -> LongitudinalMemory:
    return LongitudinalMemory(db_path=tmp_path / "test_contra.db")


@pytest.fixture
def engine(memory: LongitudinalMemory) -> ContradictionEngine:
    return ContradictionEngine(memory=memory)


class TestContradictionTypes:
    def test_contradiction_construct(self) -> None:
        c = Contradiction(
            id="c1",
            kind="value_vs_decision",
            description="freedom vs. security",
            side_a="I value freedom",
            side_b="I chose a stable job",
        )
        assert c.id == "c1"
        assert c.is_active()
        assert c.epistemic_status == EpistemicStatus.INTERPRETATION
        assert len(c.interpretations) == 0

    def test_detection_is_empty(self) -> None:
        d = ContradictionDetection()
        assert d.is_empty()
        d.contradictions.append(
            Contradiction(
                id="c1",
                kind="value_vs_decision",
                description="test",
                side_a="a",
                side_b="b",
            )
        )
        assert not d.is_empty()


class TestContradictionDetector:
    def test_no_contradictions_on_empty_memory(self, memory: LongitudinalMemory) -> None:
        detector = ContradictionDetector(memory=memory)
        detection = detector.detect_all(user_id="alice")
        assert isinstance(detection, ContradictionDetection)
        assert len(detection.contradictions) == 0
        assert len(detection.notes) >= 1

    def test_value_vs_decision_detected(self, memory: LongitudinalMemory) -> None:
        memory.add(
            kind="declared_value",
            text="Freedom and autonomy are my highest values.",
            user_id="alice",
        )
        memory.add(
            kind="decision",
            text="I chose the stable corporate job for the security.",
            user_id="alice",
        )
        detector = ContradictionDetector(memory=memory)
        contradictions = detector.detect_value_vs_decisions(user_id="alice")
        assert len(contradictions) >= 1
        c = contradictions[0]
        assert c.kind == "value_vs_decision"
        assert "freedom" in c.side_a.lower()
        assert "stable" in c.side_b.lower() or "security" in c.side_b.lower()
        # Must include multiple interpretations (not shaming)
        assert len(c.interpretations) >= 3

    def test_no_contradiction_when_no_opposing_values(self, memory: LongitudinalMemory) -> None:
        memory.add(
            kind="declared_value",
            text="I value freedom.",
            user_id="alice",
        )
        memory.add(
            kind="decision",
            text="I quit my job to travel freely.",
            user_id="alice",
        )
        detector = ContradictionDetector(memory=memory)
        contradictions = detector.detect_value_vs_decisions(user_id="alice")
        assert len(contradictions) == 0

    def test_intra_statement_contradiction(self, memory: LongitudinalMemory) -> None:
        detector = ContradictionDetector(memory=memory)
        contradictions = detector.detect_intra_statement(
            "Part of me wants to leave, but another part wants to stay.",
            user_id="alice",
        )
        assert len(contradictions) >= 1
        assert contradictions[0].kind == "intra_statement"

    def test_intra_statement_no_false_positive(self, memory: LongitudinalMemory) -> None:
        detector = ContradictionDetector(memory=memory)
        contradictions = detector.detect_intra_statement(
            "I want to leave my job.",
            user_id="alice",
        )
        assert len(contradictions) == 0

    def test_detect_all_combines(self, memory: LongitudinalMemory) -> None:
        memory.add(
            kind="declared_value",
            text="Freedom is my highest value.",
            user_id="alice",
        )
        memory.add(
            kind="decision",
            text="I chose a stable secure job.",
            user_id="alice",
        )
        detector = ContradictionDetector(memory=memory)
        detection = detector.detect_all(
            user_id="alice",
            current_statement="Part of me wants to leave, but another part wants to stay.",
        )
        # Should include both value/decision and intra-statement contradictions
        kinds = {c.kind for c in detection.contradictions}
        assert "value_vs_decision" in kinds
        assert "intra_statement" in kinds


class TestContradictionEngine:
    def test_detect_returns_detection(self, engine: ContradictionEngine) -> None:
        detection = engine.detect(user_id="alice", current_statement=None)
        assert isinstance(detection, ContradictionDetection)

    def test_render_does_not_shame(self, engine: ContradictionEngine) -> None:
        memory = engine.memory
        memory.add(
            kind="declared_value",
            text="Freedom is my highest value.",
            user_id="alice",
        )
        memory.add(
            kind="decision",
            text="I chose a stable secure job.",
            user_id="alice",
        )
        detection = engine.detect(user_id="alice")
        if detection.contradictions:
            text = engine.render(detection.contradictions[0])
            assert "POSSIBLE TENSION" in text
            assert "INTERPRETATIONS" in text
            assert "not judgments" in text.lower()
            assert "You can reject it" in text

    def test_render_empty_detection(self, engine: ContradictionEngine) -> None:
        detection = engine.detect(user_id="alice")
        text = engine.render_detection(detection)
        assert "No active contradictions" in text
