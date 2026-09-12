"""FastAPI server — exposes Aletheia's engines as a clean HTTP API."""
from __future__ import annotations

from .server import app, run

__all__ = ["app", "run"]
