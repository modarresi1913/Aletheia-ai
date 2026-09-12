"""Life Experiment Engine — converts insight into reversible real-world tests.

Core loop:
    Reflection → Experiment → Evidence → Revision → Action

The engine generates small, reversible experiments calibrated to the user's
situation. Experiments are NOT endless introspection; they are designed to
produce evidence that updates hypotheses.
"""
from __future__ import annotations

from .engine import ExperimentEngine
from .types import ExperimentOutcome, LifeExperiment

__all__ = ["ExperimentEngine", "ExperimentOutcome", "LifeExperiment"]
