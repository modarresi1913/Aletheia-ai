"""Example: Socratic question generation.

Run: python examples/02_socratic.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aletheia.llm.mock import MockProvider  # noqa: E402
from aletheia.socratic.engine import SocraticEngine  # noqa: E402


def main() -> None:
    statement = (
        "I'm afraid of disappointing my parents by changing my career."
    )

    print("=" * 72)
    print("EXAMPLE 2 — Socratic Questions")
    print("=" * 72)
    print(f"\nUser statement:\n  {statement!r}\n")

    engine = SocraticEngine(llm=MockProvider(), max_questions=3)
    questions = engine.generate(statement)

    for i, q in enumerate(questions, 1):
        print(f"Question {i}:")
        print(f"  text        : {q.text}")
        print(f"  purpose     : {q.purpose}")
        print(f"  layer       : {q.targeted_layer.value if q.targeted_layer else '-'}")
        print(f"  status      : {q.epistemic_status.value}")
        print(f"  open-ended  : {q.is_open}")
        print()


if __name__ == "__main__":
    main()
