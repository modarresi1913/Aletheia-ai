"""Pytest configuration."""
import os
import sys
from pathlib import Path

# Ensure src/ is on the path even without installation
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Force the mock LLM provider for all tests by default
os.environ.setdefault("ALETHEIA_LLM_PROVIDER", "mock")
os.environ.setdefault("ALETHEIA_ENV", "development")
os.environ.setdefault("ALETHEIA_SAFETY_CONSTITUTION_ENFORCE", "true")
