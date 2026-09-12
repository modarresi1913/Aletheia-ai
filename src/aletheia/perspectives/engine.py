"""Multi-Perspective Engine.

Maps user statements to multiple intellectual lenses via the Wisdom Graph.
Each perspective is clearly labeled and epistemically marked.
"""
from __future__ import annotations

from collections.abc import Iterable

import structlog

from ..core.types import EpistemicStatus
from ..wisdom.graph import WisdomGraph
from ..wisdom.retrieval import WisdomRetriever
from .types import Perspective, PerspectiveCategory, PerspectiveName, PerspectiveView

log = structlog.get_logger(__name__)


# Mapping: tradition_id in Wisdom Graph -> (PerspectiveName, PerspectiveCategory)
_TRADITION_TO_PERSPECTIVE: dict[str, tuple[PerspectiveName, PerspectiveCategory]] = {
    "stoicism": ("Stoic", "philosophy"),
    "zen": ("Zen", "philosophy"),
    "sufism": ("Sufi", "mysticism"),
    "taoism": ("Taoist", "philosophy"),
    "vedanta": ("Vedantic", "philosophy"),
    "existentialism": ("Existential", "philosophy"),
    "christian_mysticism": ("Christian Mystical", "mysticism"),
    "kabbalah": ("Kabbalistic", "mysticism"),
    "depth_psychology": ("Psychological", "psychology"),
    "cognitive_science": ("Scientific", "science"),
}


class MultiPerspectiveEngine:
    """Generates multi-perspective views via the Wisdom Graph."""

    def __init__(
        self,
        graph: WisdomGraph | None = None,
        retriever: WisdomRetriever | None = None,
    ) -> None:
        self.graph = graph or WisdomGraph.default()
        self.retriever = retriever or WisdomRetriever(self.graph, top_k=8)

    def view_through(
        self,
        perspective_name: PerspectiveName,
        statement: str,
    ) -> Perspective:
        """Generate a single perspective on the statement."""
        # Find the tradition_id for this perspective
        tradition_id = self._perspective_to_tradition(perspective_name)
        if tradition_id is None:
            # Practical, Ethical, Scientific not tied to a single tradition
            return self._non_tradition_perspective(perspective_name, statement)

        # Retrieve wisdom claims from this tradition relevant to the statement
        all_claims = self.retriever.retrieve(statement, top_k=8)
        supporting = [c for c in all_claims if c.tradition == tradition_id]

        if not supporting:
            return Perspective(
                name=perspective_name,
                category=_TRADITION_TO_PERSPECTIVE[tradition_id][1],
                tradition_id=tradition_id,
                text=(
                    f"[PHILOSOPHICAL-VIEW] The {perspective_name} tradition does not "
                    f"have a directly relevant claim in the Wisdom Graph for this statement. "
                    "This is a limitation of the graph, not of the tradition."
                ),
                notes=["No supporting claim found in the Wisdom Graph seed."],
            )

        # Compose the perspective text from the supporting claims
        primary = supporting[0]
        text_parts = [
            f"[PHILOSOPHICAL-VIEW] From the {perspective_name} tradition:",
            primary.text,
        ]
        if primary.citation.author or primary.citation.work:
            src_parts = [p for p in [primary.citation.author, primary.citation.work, primary.citation.locator] if p]
            text_parts.append(f"  — {' '.join(src_parts)}")

        # Surface counterclaims explicitly
        counter_perspectives: list[str] = []
        for cc_id in primary.counterclaims:
            cc = self.graph.get_claim(cc_id)
            if cc:
                counter_perspectives.append(
                    f"[{cc.tradition}] {cc.text}"
                )

        return Perspective(
            name=perspective_name,
            category=_TRADITION_TO_PERSPECTIVE[tradition_id][1],
            tradition_id=tradition_id,
            text="\n".join(text_parts),
            epistemic_status=EpistemicStatus.PHILOSOPHICAL_VIEW,
            citation=primary.citation,
            supporting_claims=supporting,
            counter_perspectives=counter_perspectives,
        )

    def all_perspectives(
        self,
        statement: str,
        include: Iterable[PerspectiveName] | None = None,
    ) -> PerspectiveView:
        """Generate all available perspectives for a statement.

        Args:
            statement: The user's statement.
            include: Optional iterable of perspective names to include.
                     If None, all available perspectives are included.
        """
        if include is None:
            names: list[PerspectiveName] = [
                "Stoic", "Zen", "Sufi", "Taoist", "Existential",
                "Vedantic", "Psychological", "Scientific", "Practical",
            ]
        else:
            names = list(include)

        perspectives: list[Perspective] = []
        for name in names:
            try:
                p = self.view_through(name, statement)
                perspectives.append(p)
            except Exception as e:
                log.warning("perspective.generation_failed", name=name, error=str(e))

        # Detect disagreements
        disagreements = self._detect_disagreements(perspectives)

        return PerspectiveView(
            statement=statement,
            perspectives=perspectives,
            disagreements=disagreements,
            notes=[
                "Each perspective is labeled. Philosophical/spiritual traditions "
                "are presented as PHILOSOPHICAL-VIEW, never as FACT.",
                "Disagreements between traditions are preserved, not collapsed.",
            ],
        )

    def render_view(self, view: PerspectiveView) -> str:
        """Render a multi-perspective view as readable text."""
        lines = [
            "MULTI-PERSPECTIVE VIEW",
            "=" * 60,
            f"statement: {view.statement!r}",
            "",
        ]
        for p in view.perspectives:
            lines.append(f"── {p.name} ({p.category}) ──────────────────────")
            lines.append(p.text)
            if p.counter_perspectives:
                lines.append("  Counter-perspectives:")
                for cp in p.counter_perspectives:
                    lines.append(f"    - {cp}")
            lines.append("")

        if view.disagreements:
            lines.append("── DISAGREEMENTS (preserved, not resolved) ──────")
            for d in view.disagreements:
                lines.append(f"  - {d}")
            lines.append("")

        if view.notes:
            lines.append("Notes:")
            for n in view.notes:
                lines.append(f"  - {n}")

        return "\n".join(lines)

    # ── internals ─────────────────────────────────────────────

    @staticmethod
    def _perspective_to_tradition(name: PerspectiveName) -> str | None:
        for tid, (pname, _) in _TRADITION_TO_PERSPECTIVE.items():
            if pname == name:
                return tid
        return None

    def _non_tradition_perspective(
        self,
        name: PerspectiveName,
        statement: str,
    ) -> Perspective:
        """Generate a non-tradition perspective (Practical, Ethical, Scientific)."""
        if name == "Practical":
            return Perspective(
                name=name,
                category="practical",
                text=(
                    "[PLAUSIBLE] From a practical perspective:\n"
                    "  - What concrete, observable situation are you in?\n"
                    "  - What reversible intermediate steps exist before any irreversible action?\n"
                    "  - What is the smallest experiment that could yield information?\n"
                    "  - What would you do if the decision could be reversed in 30 days?"
                ),
                epistemic_status=EpistemicStatus.PLAUSIBLE,
                notes=[
                    "Practical perspective is action-oriented, not interpretive.",
                    "It assumes the user is the authority on their own situation.",
                ],
            )
        if name == "Ethical":
            return Perspective(
                name=name,
                category="ethical",
                text=(
                    "[INTERPRETATION] From an ethical perspective:\n"
                    "  - Who else is affected by this situation?\n"
                    "  - How might they describe it differently?\n"
                    "  - Are there perspectives not represented in the current statement?\n"
                    "  - What would change if you considered the situation from their side?"
                ),
                epistemic_status=EpistemicStatus.INTERPRETATION,
                notes=[
                    "Ethical perspective expands the frame beyond the user's first-person view.",
                ],
            )
        if name == "Scientific":
            # Use cognitive science tradition if available
            tradition_id = "cognitive_science"
            claims = self.retriever.retrieve(statement, top_k=5)
            sci_claims = [c for c in claims if c.tradition == tradition_id]
            if not sci_claims:
                return Perspective(
                    name=name,
                    category="science",
                    text=(
                        "[UNKNOWN] The scientific perspective on this specific statement "
                        "is not represented in the current Wisdom Graph seed. "
                        "Cognitive science would typically examine: prediction error, "
                        "learned reward patterns, and socially-conditioned responses."
                    ),
                    epistemic_status=EpistemicStatus.UNKNOWN,
                )
            primary = sci_claims[0]
            return Perspective(
                name=name,
                category="science",
                tradition_id=tradition_id,
                text=(
                    f"[{primary.epistemic_status.value}] From cognitive science:\n"
                    f"  {primary.text}\n"
                    f"  — {primary.citation.author or ''}, {primary.citation.work or ''}"
                ),
                epistemic_status=primary.epistemic_status,
                citation=primary.citation,
                supporting_claims=sci_claims,
            )
        # Fallback
        return Perspective(
            name=name,
            category="practical",
            text=f"[UNKNOWN] Perspective '{name}' is not implemented.",
            epistemic_status=EpistemicStatus.UNKNOWN,
        )

    @staticmethod
    def _detect_disagreements(perspectives: list[Perspective]) -> list[str]:
        """Surface explicit disagreements between perspectives."""
        disagreements: list[str] = []
        # If two perspectives cite claims that are counterclaims of each other, surface it
        for i, p1 in enumerate(perspectives):
            for p2 in perspectives[i + 1:]:
                for c1 in p1.supporting_claims:
                    for c2 in p2.supporting_claims:
                        if c2.id in c1.counterclaims:
                            disagreements.append(
                                f"The {p1.name} and {p2.name} perspectives disagree "
                                f"on '{c1.concept_id}'."
                            )
        return disagreements


__all__ = ["MultiPerspectiveEngine"]
