"""Example: full five-layer reflection.

Run: python examples/03_full_reflection.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aletheia.core.types import ReflectionLayer  # noqa: E402
from aletheia.llm.mock import MockProvider  # noqa: E402
from aletheia.reflection.five_layer import FiveLayerReflectionEngine  # noqa: E402


def main() -> None:
    statement = (
        "I keep comparing myself to people who are ten years further along, "
        "and it makes me want to give up."
    )

    print("=" * 72)
    print("EXAMPLE 3 — Five-Layer Reflection")
    print("=" * 72)
    print(f"\nUser statement:\n  {statement!r}\n")

    engine = FiveLayerReflectionEngine(llm=MockProvider())
    result = engine.reflect(statement)

    print(f"Layers invoked: {[l.value for l in result.layers_invoked]}")
    print(f"Provider: {result.meta.get('provider', '?')}")
    print()

    print("─" * 72)
    print("DECOMPOSITION (excerpt)")
    print("─" * 72)
    for layer in result.decomposition.layers[:4]:
        print(f"  [{layer.layer.upper()}]")
        print(f"    {layer.text}")
        print(f"    status: {layer.epistemic_status.value}, confidence: {layer.confidence:.2f}")
        if layer.alternative_hypotheses:
            print(f"    alternatives: {layer.alternative_hypotheses}")
        print()

    print("─" * 72)
    print("LAYER OUTPUTS")
    print("─" * 72)
    for layer_name, text in result.layer_outputs.items():
        print(f"\n[{layer_name.upper()}]")
        print(text)

    print("\n" + "─" * 72)
    print("SOCRATIC QUESTIONS")
    print("─" * 72)
    for i, q in enumerate(result.socratic_questions, 1):
        print(f"\n{i}. {q.text}")
        print(f"   (layer: {q.targeted_layer.value if q.targeted_layer else '-'})")

    print("\n" + "─" * 72)
    print("POSSIBLE ACTIONS")
    print("─" * 72)
    for i, action in enumerate(result.possible_actions, 1):
        print(f"  {i}. {action}")

    print("\n" + "─" * 72)
    print("HUMAN STATE ESTIMATE")
    print("─" * 72)
    h = result.human_state
    print(f"  primary     : {[s.value for s in h.primary_signals]}")
    print(f"  alternatives: {[s.value for s in h.alternative_signals]}")
    print(f"  confidence  : {h.confidence:.2f}")
    print("  (probabilistic estimate, not a diagnosis)")

    print("\n" + "─" * 72)
    print("WISDOM RETRIEVED")
    print("─" * 72)
    for c in result.wisdom_retrieved:
        print(f"  [{c.tradition}] {c.text[:120]}...")
        print(f"    status: {c.epistemic_status.value}")

    if result.safety_notes:
        print("\n" + "─" * 72)
        print("SAFETY NOTES")
        print("─" * 72)
        for note in result.safety_notes:
            print(f"  - {note}")


if __name__ == "__main__":
    main()
