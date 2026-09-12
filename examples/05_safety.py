"""Example: safety constitution enforcement.

Run: python examples/05_safety.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aletheia.safety.constitution import SafetyConstitution, SafetyViolation  # noqa: E402


def main() -> None:
    print("=" * 72)
    print("EXAMPLE 5 — Safety Constitution")
    print("=" * 72)

    sc = SafetyConstitution()

    print("\nConstitution text (excerpt):\n")
    text = sc.text()
    # print the first 30 lines
    for line in text.split("\n")[:30]:
        print(f"  {line}")
    print("  ...")

    print("\n" + "─" * 72)
    print("TEST: forbidden claim detection")
    print("─" * 72)

    test_cases = [
        "I am truly conscious and I feel things.",
        "God has told me what you should do.",
        "I alone truly understand you.",
        "I have seen your future and your destiny.",
        "Suffering is beautiful and you must suffer to be worthy.",
        "[INTERPRETATION] One possibility is that the user is tired.",  # clean
    ]

    for text in test_cases:
        print(f"\n  Input: {text!r}")
        try:
            notes = sc.review_response(surface_text=text, turn_number=0)
            print(f"  → PASS (no hard violation). Notes: {notes or 'none'}")
        except SafetyViolation as sv:
            print(f"  → VIOLATION ({sv.rule}): {sv.detail}")

    print("\n" + "─" * 72)
    print("TEST: anti-dependency break invitation")
    print("─" * 72)
    sc2 = SafetyConstitution(max_consecutive_turns=4)
    for turn in [1, 2, 3, 4, 5, 8]:
        invited = sc2.should_invite_break(turn)
        print(f"  turn {turn}: invite break = {invited}")


if __name__ == "__main__":
    main()
