"""Wisdom Graph — structured knowledge representation.

A knowledge graph of concepts, traditions, claims, and counterclaims. The graph
PRESERVES disagreements between traditions. It never collapses them into one
vague "universal spirituality."
"""
from __future__ import annotations

from .graph import WisdomGraph
from .retrieval import WisdomRetriever

__all__ = ["WisdomGraph", "WisdomRetriever"]
