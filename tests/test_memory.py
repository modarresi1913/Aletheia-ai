"""Tests for the Longitudinal Memory module (v0.3)."""
from __future__ import annotations

from pathlib import Path

import pytest

from aletheia.core.types import EpistemicStatus, HypothesisStatus
from aletheia.memory.entry import MemoryEntry
from aletheia.memory.report import ReflectionReport, ReflectionReportGenerator
from aletheia.memory.store import LongitudinalMemory


@pytest.fixture
def memory(tmp_path: Path) -> LongitudinalMemory:
    """Fresh memory store with a temp DB."""
    db_path = tmp_path / "test_memory.db"
    return LongitudinalMemory(db_path=db_path)


class TestMemoryEntry:
    def test_construct(self) -> None:
        e = MemoryEntry(
            id="mem_test1",
            kind="declared_value",
            text="Freedom is highly important to me.",
        )
        assert e.id == "mem_test1"
        assert e.kind == "declared_value"
        assert e.epistemic_status == EpistemicStatus.INTERPRETATION
        assert e.hypothesis_status == HypothesisStatus.ACTIVE
        assert e.confidence == 0.4

    def test_revise(self) -> None:
        e = MemoryEntry(id="m1", kind="hypothesis", text="User fears failure.")
        e.revise(HypothesisStatus.WEAKENED, note="Counter-evidence in session 3")
        assert e.hypothesis_status == HypothesisStatus.WEAKENED
        assert "Counter-evidence in session 3" in e.counterevidence

    def test_strengthen(self) -> None:
        e = MemoryEntry(id="m1", kind="hypothesis", text="User values autonomy.")
        e.strengthen("User reiterated value in session 4")
        assert len(e.evidence) == 1

    def test_weaken_auto_downgrades(self) -> None:
        e = MemoryEntry(id="m1", kind="hypothesis", text="User fears failure.")
        e.weaken("Counter-evidence 1")
        e.weaken("Counter-evidence 2")
        # Should auto-downgrade to WEAKENED after 2+ counterevidence
        assert e.hypothesis_status == HypothesisStatus.WEAKENED

    def test_supersede(self) -> None:
        e = MemoryEntry(id="m1", kind="hypothesis", text="Old interpretation.")
        e.supersede("m2", note="Replaced by better hypothesis")
        assert e.hypothesis_status == HypothesisStatus.SUPERSEDED
        assert e.superseded_by == "m2"

    def test_confidence_cannot_exceed_0_94(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            MemoryEntry(id="m", kind="hypothesis", text="test", confidence=0.99)


class TestLongitudinalMemory:
    def test_add_and_get(self, memory: LongitudinalMemory) -> None:
        entry = memory.add(
            kind="declared_value",
            text="Freedom is important.",
            user_id="alice",
        )
        assert entry.id.startswith("mem_")
        retrieved = memory.get(entry.id)
        assert retrieved is not None
        assert retrieved.text == "Freedom is important."

    def test_all_for_user_isolation(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="theme", text="alice's theme", user_id="alice")
        memory.add(kind="theme", text="bob's theme", user_id="bob")
        alice_entries = memory.all_for_user("alice")
        bob_entries = memory.all_for_user("bob")
        assert len(alice_entries) == 1
        assert len(bob_entries) == 1
        assert alice_entries[0].text == "alice's theme"

    def test_by_kind(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="declared_value", text="value 1", user_id="alice")
        memory.add(kind="decision", text="decision 1", user_id="alice")
        memory.add(kind="declared_value", text="value 2", user_id="alice")
        values = memory.declared_values("alice")
        decisions = memory.decisions("alice")
        assert len(values) == 2
        assert len(decisions) == 1

    def test_active_hypotheses(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="hypothesis", text="H1", user_id="alice")
        h2 = memory.add(kind="hypothesis", text="H2", user_id="alice")
        h2.revise(HypothesisStatus.REJECTED, "wrong")
        memory.update(h2)
        active = memory.active_hypotheses("alice")
        assert len(active) == 1
        assert active[0].text == "H1"

    def test_search(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="theme", text="User is afraid of failure", user_id="alice")
        memory.add(kind="theme", text="User values autonomy", user_id="alice")
        results = memory.search("alice", "afraid")
        assert len(results) == 1
        assert "afraid" in results[0].text.lower()

    def test_delete(self, memory: LongitudinalMemory) -> None:
        entry = memory.add(kind="theme", text="to delete", user_id="alice")
        deleted = memory.delete(entry.id)
        assert deleted is True
        assert memory.get(entry.id) is None

    def test_wipe(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="theme", text="a", user_id="alice")
        memory.add(kind="theme", text="b", user_id="alice")
        memory.add(kind="theme", text="c", user_id="bob")
        count = memory.wipe("alice")
        assert count == 2
        assert len(memory.all_for_user("alice")) == 0
        assert len(memory.all_for_user("bob")) == 1

    def test_export(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="theme", text="a", user_id="alice")
        exported = memory.export("alice")
        assert len(exported) == 1
        assert exported[0]["text"] == "a"

    def test_stats(self, memory: LongitudinalMemory) -> None:
        memory.add(kind="declared_value", text="v1", user_id="alice")
        memory.add(kind="hypothesis", text="h1", user_id="alice")
        memory.add(kind="decision", text="d1", user_id="alice")
        stats = memory.stats("alice")
        assert stats["total"] == 3
        assert stats["declared_value"] == 1
        assert stats["hypothesis"] == 1
        assert stats["active_hypotheses"] == 1

    def test_persistence_across_instances(self, tmp_path: Path) -> None:
        """Entries persist across memory instances using the same DB path."""
        db_path = tmp_path / "persist.db"
        m1 = LongitudinalMemory(db_path=db_path)
        m1.add(kind="theme", text="persistent entry", user_id="alice")
        m2 = LongitudinalMemory(db_path=db_path)
        entries = m2.all_for_user("alice")
        assert len(entries) == 1
        assert entries[0].text == "persistent entry"


class TestReflectionReport:
    def test_generate_empty(self, memory: LongitudinalMemory) -> None:
        gen = ReflectionReportGenerator(memory=memory)
        report = gen.generate(user_id="alice")
        assert isinstance(report, ReflectionReport)
        assert "memory ≠ truth" in report.disclaimer.lower() or "memory is not truth" in report.disclaimer.lower()
        assert report.recurring_themes == []

    def test_generate_with_entries(self, memory: LongitudinalMemory) -> None:
        # Add some entries
        memory.add(
            kind="declared_value",
            text="Freedom is highly important to me.",
            user_id="alice",
            tags=["freedom", "autonomy"],
        )
        memory.add(
            kind="decision",
            text="I chose a stable job for the security.",
            user_id="alice",
            tags=["security"],
        )
        memory.add(
            kind="hypothesis",
            text="User may be prioritizing security over stated freedom value.",
            user_id="alice",
            evidence=["Decision in session 3"],
        )

        gen = ReflectionReportGenerator(memory=memory)
        report = gen.generate(user_id="alice")

        assert report.user_id == "alice"
        assert len(report.recurring_themes) >= 1
        # Value/behavior tension should be detected (freedom vs. security)
        assert len(report.value_behavior_tensions) >= 1
        assert len(report.hypotheses_gained_evidence) >= 1

    def test_render_text(self, memory: LongitudinalMemory) -> None:
        gen = ReflectionReportGenerator(memory=memory)
        report = gen.generate(user_id="alice")
        text = report.render_text()
        assert "PERSONAL REFLECTION REPORT" in text
        assert "RECURRING THEMES" in text
        assert "VALUE / BEHAVIOR TENSIONS" in text
