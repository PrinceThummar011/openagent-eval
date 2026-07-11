"""ASCII art banner for OpenAgent Eval CLI."""

from __future__ import annotations

from importlib.metadata import version

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _generate_ascii_art(text: str = "oaeval") -> str:
    """Generate ASCII art text using pyfiglet.

    Falls back to a simple box if pyfiglet is not installed.

    Args:
        text: The text to render as ASCII art.

    Returns:
        ASCII art string.
    """
    try:
        import pyfiglet

        # Use a clean, modern font
        return pyfiglet.figlet_format(text, font="small")
    except ImportError:
        # Fallback when pyfiglet is not installed
        return (
            " ___   ___  \n"
            "/ __| / _ \\ \n"
            "| (__ | (_) |\n"
            " \\___| \\___/ \n"
            "              "
        )


def _get_version() -> str:
    """Get the package version.

    Returns:
        Version string.
    """
    try:
        return version("openagent-eval")
    except Exception:
        return "0.3.0"


def create_banner(console: Console | None = None, show_version: bool = True) -> None:
    """Display the OpenAgent Eval ASCII art banner with gradient styling.

    Args:
        console: Rich Console instance. Creates one if not provided.
        show_version: Whether to show the version number.
    """
    if console is None:
        console = Console()

    ascii_art = _generate_ascii_art("oaeval")
    ver = _get_version()

    # Create gradient-styled ASCII art
    lines = ascii_art.split("\n")
    gradient_art = Text()

    # Color gradient from cyan to blue
    colors = ["bold cyan", "bold cyan", "bold bright_cyan", "bold bright_blue", "bold blue"]

    for i, line in enumerate(lines):
        if line.strip():  # Only color non-empty lines
            color = colors[i % len(colors)]
            gradient_art.append(f"{line}\n", style=color)
        else:
            gradient_art.append("\n")

    # Add version and tagline
    if show_version:
        gradient_art.append(f"\n     v{ver}", style="dim white")
    gradient_art.append("\n", style="default")
    gradient_art.append("  RAG Evaluation Framework", style="italic bright_blue")
    gradient_art.append("\n  ", style="default")
    gradient_art.append("Open-source CLI for evaluating RAG systems", style="dim")

    # Create a beautiful panel
    panel = Panel(
        Align.center(gradient_art),
        border_style="bright_blue",
        padding=(1, 2),
        expand=False,
        title="[bold bright_blue]oaeval[/bold bright_blue]",
        subtitle="[dim]Press F1 for help[/dim]",
    )

    console.print()
    console.print(panel)
    console.print()


def create_mini_banner(console: Console | None = None) -> None:
    """Display a compact single-line banner with styling.

    Args:
        console: Rich Console instance. Creates one if not provided.
    """
    if console is None:
        console = Console()

    ver = _get_version()

    # Create a styled mini banner
    banner = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    banner.add_column("name", style="bold cyan")
    banner.add_column("version", style="dim white")
    banner.add_column("tagline", style="italic bright_blue")

    banner.add_row("oaeval", f"v{ver}", "RAG Evaluation Framework")

    console.print(banner)
    console.print()


def create_rich_banner(console: Console | None = None) -> None:
    """Display a rich banner with feature highlights.

    Args:
        console: Rich Console instance. Creates one if not provided.
    """
    if console is None:
        console = Console()

    ver = _get_version()

    # Create the main banner text
    banner_text = Text()
    banner_text.append("  oaeval  ", style="bold cyan")
    banner_text.append(f"v{ver}", style="dim white")
    banner_text.append("  -  ", style="dim")
    banner_text.append("RAG Evaluation Framework", style="italic bright_blue")

    # Create feature highlights as text
    features_text = Text()
    features_text.append("  Features:\n", style="bold")
    features_text.append("  [bright_blue]>[/bright_blue] Corpus Health Auditor\n", style="dim")
    features_text.append("  [bright_blue]>[/bright_blue] NLI-based Faithfulness Scoring\n", style="dim")
    features_text.append("  [bright_blue]>[/bright_blue] Component Blame Attribution\n", style="dim")
    features_text.append("  [bright_blue]>[/bright_blue] Synthetic Test Data Generation", style="dim")

    # Combine into panel
    content = Text()
    content.append_text(banner_text)
    content.append("\n\n")
    content.append_text(features_text)

    panel = Panel(
        content,
        border_style="bright_blue",
        padding=(1, 2),
        expand=False,
        title="[bold bright_blue]OpenAgent Eval[/bold bright_blue]",
        subtitle="[dim]v1.0 - Production-Grade RAG Evaluation[/dim]",
    )

    console.print()
    console.print(panel)
    console.print()
