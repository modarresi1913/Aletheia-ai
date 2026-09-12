"""Personal Reflection Report generator.

The report explicitly distinguishes memory (what was stored) from truth (what is
the case). A pattern in memory is a pattern in what Aletheia has heard, not a
fact about the user.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from ..core.types import HypothesisStatus
from .store import LongitudinalMemory


class ReflectionReport(BaseModel):
    """A periodic Personal Reflection Report.

    Every section explicitly reminds the reader that memory is not truth.
    """

    user_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recurring_themes: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    value_behavior_tensions: list[dict[str, Any]] = Field(default_factory=list)
    hypotheses_gained_evidence: list[dict[str, Any]] = Field(default_factory=list)
    hypotheses_lost_evidence: list[dict[str, Any]] = Field(default_factory=list)
    completed_experiments: list[dict[str, Any]] = Field(default_factory=list)
    changes_in_perspective: list[dict[str, Any]] = Field(default_factory=list)
    stats: dict[str, int] = Field(default_factory=dict)
    disclaimer: str = Field(
        default=(
            "This report summarizes what Aletheia has heard from you across sessions. "
            "It is NOT a profile of who you are. Memory ≠ truth. Patterns in memory "
            "are patterns in what was said, not facts about the person."
        )
    )

    def render_text(self) -> str:
        """Render the report as a readable text block."""
        lines = [
            "PERSONAL REFLECTION REPORT",
            "=" * 60,
            f"user_id: {self.user_id}",
            f"generated: {self.generated_at.isoformat()}",
            "",
            self.disclaimer,
            "",
            "─" * 60,
            "RECURRING THEMES",
            "─" * 60,
        ]
        if self.recurring_themes:
            for i, t in enumerate(self.recurring_themes, 1):
                lines.append(f"  {i}. {t}")
        else:
            lines.append("  (none yet)")

        lines += ["", "─" * 60, "UNRESOLVED QUESTIONS", "─" * 60]
        if self.unresolved_questions:
            for i, q in enumerate(self.unresolved_questions, 1):
                lines.append(f"  {i}. {q}")
        else:
            lines.append("  (none yet)")

        lines += ["", "─" * 60, "VALUE / BEHAVIOR TENSIONS", "─" * 60]
        if self.value_behavior_tensions:
            for t in self.value_behavior_tensions:
                lines.append(f"  - declared value: {t.get('value', '?')}")
                lines.append(f"    recent behavior: {t.get('behavior', '?')}")
                lines.append(f"    interpretation: {t.get('interpretation', '?')}")
                lines.append("")
        else:
            lines.append("  (none detected)")

        lines += ["─" * 60, "HYPOTHESES THAT GAINED EVIDENCE", "─" * 60]
        if self.hypotheses_gained_evidence:
            for h in self.hypotheses_gained_evidence:
                lines.append(f"  + {h.get('text', '?')}")
                lines.append(f"    evidence: {h.get('evidence_count', 0)} items")
                lines.append(f"    confidence: {h.get('confidence', 0):.2f}")
                lines.append("")
        else:
            lines.append("  (none yet)")

        lines += ["─" * 60, "HYPOTHESES THAT LOST EVIDENCE", "─" * 60]
        if self.hypotheses_lost_evidence:
            for h in self.hypotheses_lost_evidence:
                lines.append(f"  - {h.get('text', '?')}")
                lines.append(f"    counterevidence: {h.get('counterevidence_count', 0)} items")
                lines.append(f"    status: {h.get('status', '?')}")
                lines.append("")
        else:
            lines.append("  (none yet)")

        lines += ["─" * 60, "COMPLETED EXPERIMENTS", "─" * 60]
        if self.completed_experiments:
            for e in self.completed_experiments:
                lines.append(f"  - {e.get('title', '?')}")
                lines.append(f"    outcome: {e.get('outcome', '?')}")
                lines.append("")
        else:
            lines.append("  (none yet)")

        lines += ["─" * 60, "CHANGES IN PERSPECTIVE", "─" * 60]
        if self.changes_in_perspective:
            for c in self.changes_in_perspective:
                lines.append(f"  ~ {c.get('text', '?')}")
                lines.append(f"    superseded_by: {c.get('superseded_by', '?')}")
                lines.append("")
        else:
            lines.append("  (none tracked)")

        lines += ["", "─" * 60, "STATISTICS", "─" * 60]
        for k, v in self.stats.items():
            lines.append(f"  {k}: {v}")

        lines.append("")
        lines.append(
            "Remember: this is a mirror of what Aletheia has heard, "
            "not a portrait of who you are."
        )
        return "\n".join(lines)


class ReflectionReportGenerator:
    """Generates Personal Reflection Reports from longitudinal memory."""

    def __init__(self, memory: LongitudinalMemory | None = None) -> None:
        self.memory = memory or LongitudinalMemory()

    def generate(self, user_id: str = "anonymous") -> ReflectionReport:
        """Generate a full reflection report for a user."""
        all_entries = self.memory.all_for_user(user_id)
        themes = self.memory.themes(user_id)
        questions = self.memory.by_kind(user_id, "question")
        all_hypotheses = self.memory.all_hypotheses(user_id)
        values = self.memory.declared_values(user_id)
        decisions = self.memory.decisions(user_id)
        experiments = self.memory.experiments(user_id)
        perspective_changes = self.memory.by_kind(user_id, "perspective_change")

        # Recurring themes: surface top tags
        tag_counts: dict[str, int] = {}
        for e in all_entries:
            for t in e.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
        recurring = [
            f"{tag} (mentioned {count} times across sessions)"
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        # Also surface explicit theme entries
        for t in themes:
            recurring.append(t.text)

        # Unresolved questions
        unresolved = [q.text for q in questions if q.is_active()]

        # Value/behavior tensions: compare declared values to decisions
        tensions: list[dict[str, Any]] = []
        for value in values:
            if not value.is_active():
                continue
            # Look for decisions that may conflict
            for decision in decisions:
                decision_text = decision.text.lower()
                # Check if the decision text contains security-related cues
                # while the declared value emphasizes freedom/autonomy
                opposing_cues = {"security", "safe", "stable", "stability", "certain", "certainty"}
                if value.kind == "declared_value" and any(
                    cue in decision_text for cue in opposing_cues
                ) and any(kw in value.text.lower() for kw in {"freedom", "autonomy", "independence", "risk", "adventure"}):
                    tensions.append(
                        {
                            "value": value.text,
                            "behavior": decision.text,
                            "interpretation": (
                                "This does not necessarily indicate inconsistency. "
                                "It may mean the definition of the value has changed, "
                                "or that the value is in genuine tension with security needs."
                            ),
                        }
                    )

        # Hypotheses that gained evidence
        gained = [
            {
                "text": h.text,
                "evidence_count": len(h.evidence),
                "confidence": h.confidence,
            }
            for h in all_hypotheses
            if h.is_active() and len(h.evidence) >= 1
        ]

        # Hypotheses that lost evidence
        lost = [
            {
                "text": h.text,
                "counterevidence_count": len(h.counterevidence),
                "status": h.hypothesis_status.value,
            }
            for h in all_hypotheses
            if h.hypothesis_status in (HypothesisStatus.WEAKENED, HypothesisStatus.REJECTED, HypothesisStatus.SUPERSEDED)
        ]

        # Completed experiments
        completed = [
            {
                "title": e.text,
                "outcome": next(iter(e.evidence), "outcome not recorded"),
            }
            for e in experiments
            if not e.is_active() and e.evidence
        ]

        # Changes in perspective
        changes = [
            {
                "text": c.text,
                "superseded_by": c.superseded_by or "(not recorded)",
            }
            for c in perspective_changes
        ]

        return ReflectionReport(
            user_id=user_id,
            recurring_themes=recurring,
            unresolved_questions=unresolved,
            value_behavior_tensions=tensions,
            hypotheses_gained_evidence=gained,
            hypotheses_lost_evidence=lost,
            completed_experiments=completed,
            changes_in_perspective=changes,
            stats=self.memory.stats(user_id),
        )


__all__ = ["ReflectionReport", "ReflectionReportGenerator"]
