"""Life Experiment Engine — converts insight into reversible real-world tests.

MVP scope note: This module is a typed interface stub. Full implementation
(generating structured, safe, reversible experiments; tracking outcomes;
feeding evidence back into the Wisdom Graph and Memory) is planned for v0.3.

Core loop:
    Reflection → Experiment → Evidence → Revision → Action
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from ..core.types import EpistemicStatus


@dataclass
class LifeExperiment:
    """A small, reversible real-world experiment."""

    id: str
    title: str
    hypothesis: str
    protocol: list[str]
    duration_days: int = 7
    reversible: bool = True
    epistemic_status: EpistemicStatus = EpistemicStatus.SPECULATION
    success_criteria: list[str] = field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    outcome: str | None = None

    def start(self) -> None:
        self.start_date = date.today()
        self.end_date = self.start_date + timedelta(days=self.duration_days)

    def complete(self, outcome: str) -> None:
        self.outcome = outcome
        if not self.end_date:
            self.end_date = date.today()


@dataclass
class ExperimentEngine:
    """Stub engine. Real implementation will generate experiments via the LLM."""

    def propose(self, statement: str, *args: Any, **kwargs: Any) -> list[LifeExperiment]:
        """Return a single stub experiment.

        Real v0.3 implementation will use the LLM + reflection result to propose
        3-5 small reversible experiments calibrated to the user's situation.
        """
        return [
            LifeExperiment(
                id="exp_observation_7d",
                title="Seven-day observation period",
                hypothesis="The situation may appear different after a week of structured observation.",
                protocol=[
                    "Each evening, write down one observable event from the day.",
                    "Mark each event as OBSERVATION or INTERPRETATION.",
                    "After seven days, re-read and ask: what pattern, if any, is visible?",
                ],
                duration_days=7,
                reversible=True,
                success_criteria=[
                    "At least 5 of 7 days have an entry.",
                    "Each entry distinguishes observation from interpretation.",
                ],
            ),
            LifeExperiment(
                id="exp_two_futures",
                title="Two parallel future narratives",
                hypothesis="Writing out both paths concretely will clarify which one is actually yours.",
                protocol=[
                    "Write a 1-page narrative of your life 3 years from now if you choose path A.",
                    "Write a 1-page narrative of your life 3 years from now if you choose path B.",
                    "Re-read both in one week. Note which one feels more like yours.",
                ],
                duration_days=7,
                reversible=True,
                success_criteria=["Both narratives are written.", "Re-read occurs at the planned time."],
            ),
        ]


__all__ = ["ExperimentEngine", "LifeExperiment"]
