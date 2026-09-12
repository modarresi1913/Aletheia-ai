"""Contradiction Engine — tracks recurring value/behavior tensions.

The engine NEVER uses contradictions to shame the user. Instead, it surfaces
patterns and offers multiple interpretations:
- The definition of the value may have changed
- The value may be in genuine tension with another value (e.g., freedom vs. security)
- The behavior may be fear-driven deviation from the stated value
- The "value" may be aspirational rather than actual
"""
from __future__ import annotations

from .engine import ContradictionEngine
from .types import Contradiction, ContradictionDetection

__all__ = ["Contradiction", "ContradictionDetection", "ContradictionEngine"]
