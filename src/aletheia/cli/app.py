"""Aletheia interactive CLI.

Usage:
    aletheia                # start interactive reflective dialogue
    aletheia reflect "..."  # one-shot reflection
    aletheia decompose "..." # one-shot epistemic decomposition
    aletheia questions "..." # one-shot Socratic questions
    aletheia wisdom          # show Wisdom Graph summary
    aletheia constitution    # print the safety constitution

The CLI uses `rich` for rendering. It is the primary human-facing surface of
the MVP alongside the HTTP API.
"""
from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

from .. import __version__
from ..epistemic.decomposition import EpistemicDecomposer
from ..reflection.five_layer import FiveLayerReflectionEngine
from ..safety.constitution import SafetyConstitution
from ..socratic.engine import SocraticEngine
from ..wisdom.graph import WisdomGraph

console = Console()


BANNER = f"""
╭─────────────────────────────────────────────────────────╮
│  Aletheia AI — Reflective Intelligence Architecture    │
│  v{__version__}                                           │
│  An instrument for examining what is thinking through  │
│  you. Not a guru. Not a therapist. An instrument.      │
╰─────────────────────────────────────────────────────────╯
"""


# ─────────────────────────────────────────────────────────────
# Click command group
# ─────────────────────────────────────────────────────────────


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="aletheia")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Aletheia — reflective intelligence CLI."""
    if ctx.invoked_subcommand is None:
        # default: interactive mode
        interactive()


@cli.command()
@click.argument("statement")
def reflect(statement: str) -> None:
    """Run a full five-layer reflection on STATEMENT."""
    engine = FiveLayerReflectionEngine()
    result = engine.reflect(statement)
    _render_reflection(result)


@cli.command()
@click.argument("statement")
def decompose(statement: str) -> None:
    """Run an epistemic decomposition on STATEMENT."""
    decomposer = EpistemicDecomposer()
    d = decomposer.decompose(statement)
    console.print(decomposer.render(d))


@cli.command(name="questions")
@click.argument("statement")
@click.option("--n", default=3, show_default=True, help="Number of questions to generate.")
def questions(statement: str, n: int) -> None:
    """Generate Socratic questions for STATEMENT."""
    engine = SocraticEngine(max_questions=n)
    qs = engine.generate(statement, max_questions=n)
    if not qs:
        console.print("[dim]No questions generated.[/dim]")
        return
    for i, q in enumerate(qs, 1):
        console.print(
            Panel(
                f"[bold]{q.text}[/bold]\n\n"
                f"[dim]purpose: {q.purpose}[/dim]\n"
                f"[dim]layer: {q.targeted_layer.value if q.targeted_layer else '-'}[/dim]\n"
                f"[dim]status: {q.epistemic_status.value}[/dim]",
                title=f"Question {i}",
                border_style="cyan",
            )
        )


@cli.command()
def wisdom() -> None:
    """Show the Wisdom Graph summary."""
    g = WisdomGraph.default()
    console.print(g.render_summary())


@cli.command()
def constitution() -> None:
    """Print the Aletheia Safety Constitution."""
    c = SafetyConstitution()
    console.print(Markdown(c.text()))


@cli.command()
def health() -> None:
    """Show project health (provider, db, wisdom graph stats)."""
    from ..core.config import get_settings
    s = get_settings()
    g = WisdomGraph.default()
    table = Table(title="Aletheia Health")
    table.add_column("component", style="cyan")
    table.add_column("value", style="white")
    table.add_row("version", __version__)
    table.add_row("env", s.env)
    table.add_row("llm_provider", s.llm_provider)
    table.add_row("db_provider", s.db_provider)
    table.add_row("safety_enforced", str(s.safety_constitution_enforce))
    table.add_row("wisdom_traditions", str(len(g.traditions)))
    table.add_row("wisdom_concepts", str(len(g.concepts)))
    table.add_row("wisdom_claims", str(len(g.claims)))
    console.print(table)


# ─────────────────────────────────────────────────────────────
# Interactive mode
# ─────────────────────────────────────────────────────────────


def interactive() -> None:
    """Start an interactive reflective dialogue."""
    console.print(BANNER, style="cyan")
    console.print(
        "[dim]Type a statement to reflect on. "
        "Type 'exit' (or Ctrl+D) to quit. "
        "Type 'help' for commands.[/dim]\n"
    )

    engine = FiveLayerReflectionEngine()
    safety = SafetyConstitution()
    history: list[dict[str, str]] = []
    turn = 0

    while True:
        try:
            user_input = Prompt.ask("[bold green]you[/bold green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]exiting.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", ":q"}:
            console.print("[dim]exiting.[/dim]")
            break
        if user_input.lower() == "help":
            _show_help()
            continue
        if user_input.lower() == "constitution":
            console.print(Markdown(safety.text()))
            continue
        if user_input.lower() == "wisdom":
            console.print(engine.wisdom_graph.render_summary())
            continue

        history.append({"role": "user", "content": user_input})
        turn += 1

        try:
            result = engine.reflect(
                user_statement=user_input,
                conversation_history=history,
            )
        except Exception as e:
            console.print(f"[red]error:[/red] {e}")
            history.pop()
            turn -= 1
            continue

        _render_reflection(result, turn=turn)

        # Anti-dependency reminder
        if safety.should_invite_break(turn):
            console.print(
                Panel(
                    "[yellow]You have been in this conversation for a while. "
                    "Consider taking a break, talking to a human, or reflecting independently. "
                    "The better Aletheia works, the less you need it.[/yellow]",
                    title="Anti-dependency",
                    border_style="yellow",
                )
            )

        history.append({"role": "assistant", "content": result.layer_outputs.get("epistemic", "")})


def _render_reflection(result, turn: int = 0) -> None:
    """Render a ReflectionResult with rich panels."""
    console.print(Rule(f"turn {turn} — reflection", style="dim cyan"))

    # Decomposition
    decomposer = EpistemicDecomposer()
    console.print(decomposer.render(result.decomposition))

    # Layer outputs
    for layer_name, text in result.layer_outputs.items():
        console.print(
            Panel(
                text,
                title=f"layer: {layer_name}",
                border_style="magenta",
            )
        )

    # Socratic questions
    if result.socratic_questions:
        for i, q in enumerate(result.socratic_questions, 1):
            console.print(
                Panel(
                    f"[bold]{q.text}[/bold]\n\n"
                    f"[dim]purpose: {q.purpose}[/dim]\n"
                    f"[dim]layer: {q.targeted_layer.value if q.targeted_layer else '-'}[/dim]",
                    title=f"question {i}",
                    border_style="cyan",
                )
            )

    # Wisdom retrieved
    if result.wisdom_retrieved:
        wtable = Table(title="wisdom retrieved", show_lines=False)
        wtable.add_column("tradition", style="cyan")
        wtable.add_column("claim", overflow="fold")
        wtable.add_column("status", style="dim")
        for c in result.wisdom_retrieved:
            wtable.add_row(c.tradition, c.text[:120] + ("…" if len(c.text) > 120 else ""), c.epistemic_status.value)
        console.print(wtable)

    # Possible actions
    if result.possible_actions:
        console.print("[bold]possible actions:[/bold]")
        for i, a in enumerate(result.possible_actions, 1):
            console.print(f"  {i}. {a}")

    # Human state
    if result.human_state.primary_signals:
        sigs = ", ".join(s.value for s in result.human_state.primary_signals)
        alts = ", ".join(s.value for s in result.human_state.alternative_signals) or "—"
        console.print(
            Panel(
                f"primary: [bold]{sigs}[/bold]\n"
                f"alternatives: [dim]{alts}[/dim]\n"
                f"confidence: [dim]{result.human_state.confidence:.2f}[/dim]\n\n"
                "[dim]This is a probabilistic estimate, not a diagnosis.[/dim]",
                title="estimated signals",
                border_style="dim",
            )
        )

    # Safety notes
    if result.safety_notes:
        for n in result.safety_notes:
            console.print(f"[yellow]safety note:[/yellow] {n}")


def _show_help() -> None:
    console.print(
        Panel(
            "[bold]commands[/bold]\n"
            "  [cyan]help[/cyan]          — show this help\n"
            "  [cyan]constitution[/cyan]  — print the safety constitution\n"
            "  [cyan]wisdom[/cyan]        — show the Wisdom Graph summary\n"
            "  [cyan]exit[/cyan]          — quit (or Ctrl+D)\n\n"
            "[bold]any other text[/bold] is treated as a statement to reflect on.",
            title="Aletheia CLI",
            border_style="cyan",
        )
    )


def main() -> None:
    """Entrypoint for the `aletheia` console script."""
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
