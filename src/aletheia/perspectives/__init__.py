"""Multi-Perspective Engine — view an issue through multiple intellectual lenses.

The engine:
- Clearly labels each perspective (Stoic, Zen, Sufi, Taoist, Existential, etc.)
- Retrieves attributed, sourced views from the Wisdom Graph
- NEVER presents philosophical or spiritual traditions as scientific facts
- NEVER fabricates quotations
- Preserves disagreements between traditions
"""
from __future__ import annotations

from .engine import MultiPerspectiveEngine
from .types import Perspective, PerspectiveView

__all__ = ["MultiPerspectiveEngine", "Perspective", "PerspectiveView"]
