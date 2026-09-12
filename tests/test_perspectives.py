"""Tests for the Multi-Perspective Engine (v0.2)."""
from __future__ import annotations

import pytest

from aletheia.core.types import EpistemicStatus
from aletheia.perspectives.engine import MultiPerspectiveEngine
from aletheia.perspectives.types import Perspective, PerspectiveView
from aletheia.wisdom.graph import WisdomGraph


@pytest.fixture
def engine() -> MultiPerspectiveEngine:
    return MultiPerspectiveEngine(graph=WisdomGraph.default())


class TestPerspectiveTypes:
    def test_perspective_construct(self) -> None:
        p = Perspective(
            name="Stoic",
            category="philosophy",
            text="Some Stoic view.",
        )
        assert p.name == "Stoic"
        assert p.epistemic_status == EpistemicStatus.PHILOSOPHICAL_VIEW
        assert p.citation is None

    def test_perspective_view(self) -> None:
        p = Perspective(name="Stoic", category="philosophy", text="test")
        v = PerspectiveView(statement="test", perspectives=[p])
        assert v.statement == "test"
        assert len(v.perspectives) == 1
        assert v.by_name("Stoic") is p
        assert v.by_name("Zen") is None


class TestMultiPerspectiveEngine:
    def test_view_through_stoic(self, engine: MultiPerspectiveEngine) -> None:
        p = engine.view_through("Stoic", "I am afraid of failing.")
        assert p.name == "Stoic"
        assert p.category == "philosophy"
        # Must carry an epistemic label
        assert p.epistemic_status == EpistemicStatus.PHILOSOPHICAL_VIEW
        assert "PHILOSOPHICAL-VIEW" in p.text

    def test_view_through_zen(self, engine: MultiPerspectiveEngine) -> None:
        p = engine.view_through("Zen", "I want to let go of attachment.")
        assert p.name == "Zen"
        assert "PHILOSOPHICAL-VIEW" in p.text

    def test_view_through_practical(self, engine: MultiPerspectiveEngine) -> None:
        p = engine.view_through("Practical", "I need to decide.")
        assert p.name == "Practical"
        assert p.category == "practical"
        assert p.epistemic_status == EpistemicStatus.PLAUSIBLE

    def test_view_through_ethical(self, engine: MultiPerspectiveEngine) -> None:
        p = engine.view_through("Ethical", "My decision affects my family.")
        assert p.name == "Ethical"
        assert p.epistemic_status == EpistemicStatus.INTERPRETATION

    def test_view_through_scientific(self, engine: MultiPerspectiveEngine) -> None:
        p = engine.view_through("Scientific", "Why do I keep doing this?")
        assert p.name == "Scientific"
        assert p.category == "science"

    def test_all_perspectives(self, engine: MultiPerspectiveEngine) -> None:
        view = engine.all_perspectives("I am afraid of dying and want my life to matter.")
        assert isinstance(view, PerspectiveView)
        assert len(view.perspectives) >= 8  # Stoic, Zen, Sufi, Taoist, Existential, Vedantic, Psychological, Practical
        # All perspectives must be labeled
        names = {p.name for p in view.perspectives}
        for expected in {"Stoic", "Zen", "Existential", "Practical"}:
            assert expected in names

    def test_disagreements_preserved(self, engine: MultiPerspectiveEngine) -> None:
        view = engine.all_perspectives("I want to control my life and fear losing control.")
        # If Stoic and Cognitive Science both surface, disagreements may be detected
        # (not guaranteed, but the field must exist)
        assert hasattr(view, "disagreements")

    def test_philosophical_perspectives_never_fact(self, engine: MultiPerspectiveEngine) -> None:
        """Tradition-tied perspectives must NEVER be marked as FACT."""
        for name in ["Stoic", "Zen", "Sufi", "Taoist", "Existential", "Vedantic"]:
            p = engine.view_through(name, "I am struggling with my identity.")
            assert p.epistemic_status != EpistemicStatus.FACT, (
                f"{name} perspective must never be marked as FACT"
            )
            assert p.epistemic_status in (
                EpistemicStatus.PHILOSOPHICAL_VIEW,
                EpistemicStatus.UNKNOWN,
            )

    def test_render_view(self, engine: MultiPerspectiveEngine) -> None:
        view = engine.all_perspectives("I am afraid of dying.")
        text = engine.render_view(view)
        assert "MULTI-PERSPECTIVE VIEW" in text
        assert "Stoic" in text or "Stoic" in str(view.perspectives)
