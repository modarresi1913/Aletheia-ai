"""Example: Wisdom Graph exploration.

Run: python examples/04_wisdom_graph.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aletheia.wisdom.graph import WisdomGraph  # noqa: E402
from aletheia.wisdom.retrieval import WisdomRetriever  # noqa: E402


def main() -> None:
    print("=" * 72)
    print("EXAMPLE 4 — Wisdom Graph")
    print("=" * 72)

    graph = WisdomGraph.default()
    print(graph.render_summary())

    print("\n" + "─" * 72)
    print("DISAGREEMENT EXAMPLE: control")
    print("─" * 72)
    for claim in graph.claims_for_concept("control"):
        print(f"\n  [{claim.tradition}] {claim.text}")
        print(f"    status: {claim.epistemic_status.value}")
        if claim.counterclaims:
            print(f"    counterclaims:")
            for cc_id in claim.counterclaims:
                cc = graph.get_claim(cc_id)
                if cc:
                    print(f"      - [{cc.tradition}] {cc.text[:100]}...")

    print("\n" + "─" * 72)
    print("RETRIEVAL: 'I am afraid of dying and want my life to matter'")
    print("─" * 72)
    retriever = WisdomRetriever(graph, top_k=5)
    for claim in retriever.retrieve("I am afraid of dying and want my life to matter"):
        print(f"\n  [{claim.tradition}] {claim.text}")
        print(f"    status: {claim.epistemic_status.value}")
        print(f"    citation: {claim.citation.author or ''}, {claim.citation.work or ''}")


if __name__ == "__main__":
    main()
