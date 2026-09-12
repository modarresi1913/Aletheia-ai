"""Longitudinal Memory — privacy-first semantic memory.

Critical principle: memory ≠ truth. Stored entries are revisable hypotheses
about the user, not facts about them. Every entry carries an epistemic status
and a revisable hypothesis lifecycle.

v0.3 implementation:
- SQLite persistence (JSONL fallback for ephemeral mode)
- Personal Reflection Report generation
- Hypothesis revision tracking (active/weakened/rejected/unresolved/superseded)
- Privacy-first: per-user, no cross-user learning, auditable, deletable
"""
from __future__ import annotations

from .entry import MemoryEntry
from .report import ReflectionReport, ReflectionReportGenerator
from .store import LongitudinalMemory, get_memory

__all__ = [
    "LongitudinalMemory",
    "MemoryEntry",
    "ReflectionReport",
    "ReflectionReportGenerator",
    "get_memory",
]
