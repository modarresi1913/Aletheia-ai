"""Experiment types."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from ..core.types import EpistemicStatus

ExperimentStatus = Literal[
    "proposed",     # suggested but not started
    "active",       # currently running
    "completed",    # finished with recorded outcome
    "abandoned",    # user chose not to complete
    "superseded",   # replaced by a better experiment
]


class ExperimentOutcome(BaseModel):
    """The outcome of a completed experiment."""

    outcome: Literal[
        "hypothesis_supported",
        "hypothesis_weakened",
        "hypothesis_rejected",
        "inconclusive",
        "abandoned",
    ]
    summary: str
    evidence_collected: list[str] = Field(default_factory=list)
    next_step: str | None = None
    confidence_delta: float = Field(default=0.0, ge=-1.0, le=1.0)


class LifeExperiment(BaseModel):
    """A small, reversible real-world experiment.

    Experiments are designed to produce evidence that updates hypotheses.
    They are NOT introspection; they require action in the world.
    """

    id: str
    user_id: str = Field(default="anonymous")
    title: str
    hypothesis: str
    hypothesis_entry_id: str | None = None
    protocol: list[str] = Field(default_factory=list)
    duration_days: int = Field(default=7, ge=1, le=90)
    reversible: bool = True
    epistemic_status: EpistemicStatus = EpistemicStatus.SPECULATION
    status: ExperimentStatus = "proposed"
    success_criteria: list[str] = Field(default_factory=list)
    failure_signals: list[str] = Field(default_factory=list)
    start_date: date | None = None
    end_date: date | None = None
    outcome: ExperimentOutcome | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = Field(default_factory=list)

    def start(self) -> None:
        """Mark the experiment as started."""
        if self.status != "proposed":
            raise ValueError(f"Cannot start experiment in status '{self.status}'")
        self.status = "active"
        self.start_date = date.today()

    def complete(self, outcome: ExperimentOutcome) -> None:
        """Mark the experiment as completed with an outcome."""
        if self.status not in ("active", "proposed"):
            raise ValueError(f"Cannot complete experiment in status '{self.status}'")
        self.status = "completed"
        self.outcome = outcome
        if not self.end_date:
            self.end_date = date.today()

    def abandon(self, reason: str = "") -> None:
        """Mark the experiment as abandoned."""
        self.status = "abandoned"
        self.outcome = ExperimentOutcome(
            outcome="abandoned",
            summary=reason or "Experiment abandoned without completion.",
        )
        if not self.end_date:
            self.end_date = date.today()

    def is_active(self) -> bool:
        return self.status == "active"

    def summary(self) -> str:
        lines = [
            f"Experiment: {self.title}",
            f"  hypothesis : {self.hypothesis}",
            f"  duration   : {self.duration_days} days",
            f"  reversible : {self.reversible}",
            f"  status     : {self.status}",
        ]
        if self.outcome:
            lines.append(f"  outcome    : {self.outcome.outcome}")
            lines.append(f"  summary    : {self.outcome.summary}")
        return "\n".join(lines)


__all__ = ["ExperimentOutcome", "ExperimentStatus", "LifeExperiment"]
