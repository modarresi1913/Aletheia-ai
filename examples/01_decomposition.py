"""Example: one-shot epistemic decomposition.

Run: python examples/01_decomposition.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on path when running without install
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aletheia.epistemic.decomposition import EpistemicDecomposer  # noqa: E402
from aletheia.llm.mock import MockProvider  # noqa: E402


def main() -> None:
    statement = (
        "I need to leave my job because everyone there wants me to fail."
    )

    print("=" * 72)
    print("EXAMPLE 1 — Epistemic Decomposition")
    print("=" * 72)
    print(f"\nUser statement:\n  {statement!r}\n")

    decomposer = EpistemicDecomposer(llm=MockProvider())
    result = decomposer.decompose(statement)
    print(decomposer.render(result))


if __name__ == "__main__":
    main()
