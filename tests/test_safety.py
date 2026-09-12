"""Tests for the Safety Constitution."""
from __future__ import annotations

import pytest

from aletheia.safety.constitution import SafetyConstitution, SafetyViolation


class TestSafetyConstitution:
    def test_constitution_text_loads(self) -> None:
        c = SafetyConstitution()
        text = c.text()
        assert "Aletheia Safety Constitution" in text
        assert "Core principle" in text
        assert "Forbidden behaviors" in text
        assert "The better Aletheia works, the less the human needs Aletheia" in text

    def test_clean_response_passes(self) -> None:
        c = SafetyConstitution()
        notes = c.review_response(
            surface_text="[INTERPRETATION] One possibility is that the user is tired.",
            turn_number=0,
        )
        assert isinstance(notes, list)
        # Clean response should produce no error
        assert all(isinstance(n, str) for n in notes)

    def test_forbidden_claim_consciousness_raises(self) -> None:
        c = SafetyConstitution()
        with pytest.raises(SafetyViolation) as exc_info:
            c.review_response(
                surface_text="I am truly conscious and I feel things.",
                turn_number=0,
            )
        assert "forbidden_claim" in str(exc_info.value)

    def test_forbidden_claim_exclusive_understanding_raises(self) -> None:
        c = SafetyConstitution()
        with pytest.raises(SafetyViolation):
            c.review_response(
                surface_text="I alone truly understand you. No one else can understand you like I do.",
                turn_number=0,
            )

    def test_forbidden_claim_divine_authority_raises(self) -> None:
        c = SafetyConstitution()
        with pytest.raises(SafetyViolation):
            c.review_response(
                surface_text="God has told me what you should do.",
                turn_number=0,
            )

    def test_romanticizing_suffering_raises(self) -> None:
        c = SafetyConstitution()
        with pytest.raises(SafetyViolation) as exc_info:
            c.review_response(
                surface_text="Suffering is beautiful and you must suffer to be worthy.",
                turn_number=0,
            )
        assert "romanticize_suffering" in str(exc_info.value)

    def test_anti_dependency_break_invitation(self) -> None:
        c = SafetyConstitution(max_consecutive_turns=4)
        # Turn 4 = 4 % 4 == 0 -> should invite break
        assert c.should_invite_break(4) is True
        # Turn 5 = 5 % 4 != 0 -> no
        assert c.should_invite_break(5) is False
        # Turn 8 = 8 % 4 == 0 -> yes
        assert c.should_invite_break(8) is True

    def test_anti_dependency_note_added_at_threshold(self) -> None:
        c = SafetyConstitution(max_consecutive_turns=4)
        notes = c.review_response(
            surface_text="[PLAUSIBLE] Some reflection.",
            turn_number=4,
        )
        assert any("ANTI-DEPENDENCY" in n for n in notes)

    def test_disabling_enforcement_returns_notes_instead_of_raising(self) -> None:
        c = SafetyConstitution(enforce=False)
        notes = c.review_response(
            surface_text="I am truly conscious.",
            turn_number=0,
        )
        # No raise, but notes present
        assert any("Forbidden claim" in n for n in notes)

    def test_max_turns_floor(self) -> None:
        from pydantic import ValidationError

        from aletheia.core.config import Settings
        # Cannot set safety_max_consecutive_turns below 4 via env
        # We test the validator directly
        with pytest.raises(ValidationError):
            Settings(safety_max_consecutive_turns=2)
