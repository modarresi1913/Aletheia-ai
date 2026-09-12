"""Safety Constitution — anti-dependency rules and runtime enforcement."""
from __future__ import annotations

from .constitution import SafetyConstitution, SafetyViolation

__all__ = ["SafetyConstitution", "SafetyViolation"]
