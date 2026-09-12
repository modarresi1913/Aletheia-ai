"""Experiment Engine.

Generates small, reversible experiments calibrated to the user's situation.
Converts insight into reality: reflection → experiment → evidence → revision → action.
"""
from __future__ import annotations

import uuid
from typing import Any

import structlog

from ..core.types import EpistemicStatus, HypothesisStatus
from ..memory.store import LongitudinalMemory
from .types import ExperimentOutcome, LifeExperiment

log = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────
# Experiment templates
# ─────────────────────────────────────────────────────────────
# Each template is keyed by a "situation signature" — a set of signals that
# indicate when the template is appropriate. Templates are intentionally small,
# reversible, and evidence-producing.

_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "exp_observation_7d",
        "title": "Seven-day observation period",
        "applicable_when": {"signals": {"fear", "anger", "internal_conflict", "uncertainty"}},
        "hypothesis": (
            "The situation may appear different after a week of structured "
            "observation that separates observation from interpretation."
        ),
        "protocol": [
            "Each evening, write down one observable event from the day.",
            "Mark each event as OBSERVATION or INTERPRETATION.",
            "Note your emotional state without judging it.",
            "After seven days, re-read and ask: what pattern, if any, is visible?",
        ],
        "duration_days": 7,
        "reversible": True,
        "success_criteria": [
            "At least 5 of 7 days have an entry.",
            "Each entry distinguishes observation from interpretation.",
            "Re-read occurs at the planned time.",
        ],
        "failure_signals": [
            "Skipping more than 2 days",
            "Treating interpretations as observations",
        ],
        "tags": ["observation", "decomposition", "patience"],
    },
    {
        "id": "exp_two_futures",
        "title": "Two parallel future narratives",
        "applicable_when": {"signals": {"existential_confusion", "uncertainty", "internal_conflict"}},
        "hypothesis": (
            "Writing out both paths concretely will clarify which one is "
            "actually yours rather than the one you think you should want."
        ),
        "protocol": [
            "Write a 1-page narrative of your life 3 years from now if you choose path A.",
            "Write a 1-page narrative of your life 3 years from now if you choose path B.",
            "Describe a typical Tuesday in each future.",
            "Re-read both in one week. Note which one feels more like yours.",
        ],
        "duration_days": 7,
        "reversible": True,
        "success_criteria": [
            "Both narratives are written.",
            "Each narrative includes a typical Tuesday.",
            "Re-read occurs at the planned time.",
        ],
        "failure_signals": [
            "Writing only one narrative",
            "Refusing to re-read",
        ],
        "tags": ["narrative", "future", "decision"],
    },
    {
        "id": "exp_audience_test",
        "title": "Audience test: if nobody knew",
        "applicable_when": {"signals": {"need_for_approval", "shame", "comparison"}},
        "hypothesis": (
            "The obstacle may be the perceived audience rather than the choice itself. "
            "Removing the audience (in imagination) may clarify what you actually want."
        ),
        "protocol": [
            "For each option you are considering, ask: if nobody whose opinion "
            "matters to me would ever know about this decision, what would I choose?",
            "Write the answer for each option.",
            "Compare the 'private' answers with the 'public' answers.",
            "Note where they diverge — without judging the divergence.",
        ],
        "duration_days": 1,
        "reversible": True,
        "success_criteria": [
            "Both private and public answers are written.",
            "Divergences are noted, not resolved.",
        ],
        "failure_signals": ["Refusing to write the private answer"],
        "tags": ["audience", "approval", "authenticity"],
    },
    {
        "id": "exp_fear_removal",
        "title": "Fear-removal test",
        "applicable_when": {"signals": {"fear", "avoidance", "desire_for_control"}},
        "hypothesis": (
            "If fear were removed from the equation, a different preference might "
            "appear. This does not mean fear should be ignored; it means fear's "
            "influence should be made visible."
        ),
        "protocol": [
            "Write the option you are considering.",
            "Write: 'If I knew I could not fail, what would I choose?'",
            "Write: 'If I knew the worst outcome would happen and I would survive it, what would I choose?'",
            "Compare the two answers with your stated preference.",
            "Note: this is information, not instruction. Fear may be carrying valid signal.",
        ],
        "duration_days": 1,
        "reversible": True,
        "success_criteria": ["Both fear-removal answers are written."],
        "failure_signals": ["Refusing to engage with the hypothetical"],
        "tags": ["fear", "preference", "clarity"],
    },
    {
        "id": "exp_direct_conversation",
        "title": "One direct conversation (clarifying only)",
        "applicable_when": {"signals": {"anger", "comparison", "internal_conflict"}},
        "hypothesis": (
            "A direct conversation with the person most involved, asking only "
            "clarifying questions, may produce information that updates the current "
            "interpretation."
        ),
        "protocol": [
            "Identify the person most central to the situation.",
            "Schedule a 30-minute conversation.",
            "Ask only clarifying questions: 'What did you mean by...?' 'How did you see...?'",
            "Do not state your interpretation. Do not defend.",
            "Take notes afterward: what did you observe? What did you interpret?",
        ],
        "duration_days": 3,
        "reversible": True,
        "success_criteria": [
            "Conversation happens within 3 days.",
            "Notes are written within 24 hours.",
            "Notes separate observation from interpretation.",
        ],
        "failure_signals": [
            "Turning the conversation into an argument",
            "Skipping the notes",
        ],
        "tags": ["communication", "observation", "interpersonal"],
    },
    {
        "id": "exp_outsider_consult",
        "title": "Consult someone outside the situation",
        "applicable_when": {"signals": {"uncertainty", "existential_confusion", "internal_conflict"}},
        "hypothesis": (
            "Someone outside the situation may see a pattern that is invisible "
            "from inside it. Their perspective is not authoritative; it is one "
            "more piece of evidence."
        ),
        "protocol": [
            "Identify one person who is not involved in the situation and whose "
            "judgment you respect.",
            "Describe the situation in observable terms (no interpretation).",
            "Ask: 'What would you want to know before deciding?'",
            "Note their questions. The questions are often more useful than answers.",
        ],
        "duration_days": 5,
        "reversible": True,
        "success_criteria": [
            "Conversation happens within 5 days.",
            "You describe the situation in observable terms.",
            "Their questions are noted.",
        ],
        "failure_signals": ["Asking for advice instead of questions"],
        "tags": ["consultation", "perspective", "external"],
    },
    {
        "id": "exp_energy_tracking",
        "title": "Energy tracking",
        "applicable_when": {"signals": {"avoidance", "existential_confusion", "uncertainty"}},
        "hypothesis": (
            "Energy levels across a week may reveal what genuinely engages you, "
            "independent of what you believe should engage you."
        ),
        "protocol": [
            "Each evening for 7 days, rate your energy on a 1-10 scale.",
            "Note the activity that consumed the most energy that day.",
            "Note the activity that gave you the most energy.",
            "After 7 days, look for patterns: what consistently drains? What consistently gives?",
        ],
        "duration_days": 7,
        "reversible": True,
        "success_criteria": [
            "5 of 7 days logged.",
            "Both drain and gain activities are noted each day.",
        ],
        "failure_signals": ["Logging fewer than 4 days"],
        "tags": ["energy", "pattern", "self-knowledge"],
    },
    {
        "id": "exp_values_journal",
        "title": "Values journal",
        "applicable_when": {"signals": {"existential_confusion", "internal_conflict", "comparison"}},
        "hypothesis": (
            "Writing down what you actually chose and did each day, alongside "
            "what you said you valued, may surface tensions invisible in self-report."
        ),
        "protocol": [
            "Each evening for 7 days, write:",
            "  - One choice I made today.",
            "  - One value that choice expressed (inferred from behavior, not intent).",
            "  - One value I would have liked that choice to express.",
            "After 7 days, look for recurring gaps between expressed and desired values.",
        ],
        "duration_days": 7,
        "reversible": True,
        "success_criteria": [
            "5 of 7 days logged.",
            "Both expressed and desired values are noted.",
        ],
        "failure_signals": ["Logging fewer than 4 days"],
        "tags": ["values", "behavior", "consistency"],
    },
]


class ExperimentEngine:
    """Proposes, tracks, and completes life experiments."""

    def __init__(self, memory: LongitudinalMemory | None = None) -> None:
        self.memory = memory or LongitudinalMemory()
        # In-memory registry of proposed/active experiments (persisted to memory store)
        self._experiments: dict[str, LifeExperiment] = {}

    def propose(
        self,
        statement: str,
        signals: set[str] | None = None,
        max_proposals: int = 3,
        user_id: str = "anonymous",
    ) -> list[LifeExperiment]:
        """Propose experiments based on the user's statement and detected signals."""
        # If signals not provided, extract from statement via crude heuristic
        if signals is None:
            signals = self._extract_signals(statement)

        proposals: list[LifeExperiment] = []
        for template in _TEMPLATES:
            applicable = template["applicable_when"].get("signals", set())
            if applicable & signals:
                proposals.append(self._instantiate(template, user_id=user_id))
            if len(proposals) >= max_proposals:
                break

        # Always include the observation experiment as a baseline
        if not proposals:
            obs_template = next(t for t in _TEMPLATES if t["id"] == "exp_observation_7d")
            proposals.append(self._instantiate(obs_template, user_id=user_id))

        for p in proposals:
            self._experiments[p.id] = p
            # Also record in memory
            self.memory.add(
                kind="experiment",
                text=p.title,
                user_id=user_id,
                epistemic_status=EpistemicStatus.SPECULATION,
                tags=[*p.tags, "experiment"],
            )

        return proposals

    def get(self, experiment_id: str) -> LifeExperiment | None:
        return self._experiments.get(experiment_id)

    def all_for_user(self, user_id: str = "anonymous") -> list[LifeExperiment]:
        return [e for e in self._experiments.values() if e.user_id == user_id]

    def active_for_user(self, user_id: str = "anonymous") -> list[LifeExperiment]:
        return [e for e in self.all_for_user(user_id) if e.is_active()]

    def start(self, experiment_id: str) -> LifeExperiment:
        """Start a proposed experiment."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Unknown experiment: {experiment_id}")
        exp.start()
        return exp

    def complete(
        self,
        experiment_id: str,
        outcome: ExperimentOutcome,
    ) -> LifeExperiment:
        """Complete an experiment and record the outcome."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Unknown experiment: {experiment_id}")
        exp.complete(outcome)

        # Update the linked hypothesis in memory
        if exp.hypothesis_entry_id:
            hypothesis = self.memory.get(exp.hypothesis_entry_id)
            if hypothesis:
                if outcome.outcome == "hypothesis_supported":
                    hypothesis.strengthen(outcome.summary)
                elif outcome.outcome == "hypothesis_weakened":
                    hypothesis.weaken(outcome.summary)
                elif outcome.outcome == "hypothesis_rejected":
                    hypothesis.revise(
                        HypothesisStatus.REJECTED,
                        note=outcome.summary,
                    )
                self.memory.update(hypothesis)

        return exp

    def abandon(self, experiment_id: str, reason: str = "") -> LifeExperiment:
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Unknown experiment: {experiment_id}")
        exp.abandon(reason)
        return exp

    def render(self, experiment: LifeExperiment) -> str:
        """Render an experiment as readable text."""
        lines = [
            f"EXPERIMENT: {experiment.title}",
            "─" * 60,
            f"hypothesis: {experiment.hypothesis}",
            f"duration  : {experiment.duration_days} days",
            f"reversible: {experiment.reversible}",
            f"status    : {experiment.status}",
            "",
            "PROTOCOL:",
        ]
        for i, step in enumerate(experiment.protocol, 1):
            lines.append(f"  {i}. {step}")
        lines += ["", "SUCCESS CRITERIA:"]
        for c in experiment.success_criteria:
            lines.append(f"  - {c}")
        if experiment.failure_signals:
            lines += ["", "FAILURE SIGNALS:"]
            for f in experiment.failure_signals:
                lines.append(f"  - {f}")
        if experiment.outcome:
            lines += ["", "OUTCOME:"]
            lines.append(f"  result  : {experiment.outcome.outcome}")
            lines.append(f"  summary : {experiment.outcome.summary}")
            if experiment.outcome.next_step:
                lines.append(f"  next    : {experiment.outcome.next_step}")
        lines += ["", f"[{experiment.epistemic_status.value}] "
                       "Experiments produce evidence, not certainty."]
        return "\n".join(lines)

    # ── internals ─────────────────────────────────────────────

    @staticmethod
    def _extract_signals(statement: str) -> set[str]:
        """Crude signal extractor for when none are provided."""
        text = statement.lower()
        signals: set[str] = set()
        cues_map = {
            "fear": ["afraid", "scared", "fear", "worried", "anxious"],
            "anger": ["angry", "furious", "resent", "frustrated"],
            "uncertainty": ["confused", "don't know", "unsure", "uncertain", "torn"],
            "comparison": ["better than", "worse than", "everyone else"],
            "avoidance": ["rather not", "don't want to think", "later"],
            "internal_conflict": ["but also", "on the other hand", "part of me", "torn between"],
            "existential_confusion": ["what's the point", "meaning", "why am i", "purpose"],
            "shame": ["ashamed", "embarrassed", "humiliated", "stupid"],
            "need_for_approval": ["what will they think", "approval", "prove myself"],
            "desire_for_control": ["must", "have to", "in control"],
        }
        for sig, cues in cues_map.items():
            if any(cue in text for cue in cues):
                signals.add(sig)
        return signals or {"uncertainty"}

    @staticmethod
    def _instantiate(template: dict[str, Any], user_id: str = "anonymous") -> LifeExperiment:
        return LifeExperiment(
            id=f"{template['id']}_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            title=template["title"],
            hypothesis=template["hypothesis"],
            protocol=template["protocol"],
            duration_days=template["duration_days"],
            reversible=template["reversible"],
            epistemic_status=EpistemicStatus.SPECULATION,
            success_criteria=template["success_criteria"],
            failure_signals=template.get("failure_signals", []),
            tags=template.get("tags", []),
        )


__all__ = ["ExperimentEngine"]
