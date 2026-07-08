"""Main CLI entry point for OpenAgent Eval."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from openagent_eval import __version__
from openagent_eval.exceptions import ConfigurationError

app = typer.Typer(
    name="oaeval",
    help="Open-source CLI framework for evaluating RAG systems and AI Agents.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"oaeval version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """OpenAgent Eval - Evaluate RAG systems and AI Agents."""


@app.command()
def init(
    config_path: str = typer.Option(
        "config.yaml",
        "--config",
        "-c",
        help="Path to create configuration file.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration file.",
    ),
) -> None:
    """Create a new evaluation configuration file."""
    path = Path(config_path)

    if path.exists() and not force:
        if not Confirm.ask(f"Configuration file '{config_path}' already exists. Overwrite?"):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        console.print(f"[green]OK[/green] Configuration created: {config_path}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  1. Edit the configuration file")
        console.print("  2. Run [bold]oaeval run[/bold] to start evaluation")
    except Exception as e:
        raise ConfigurationError(
            message=f"Failed to create configuration: {e}",
            config_path=config_path,
        ) from e


@app.command()
def run(
    config_path: str = typer.Argument(
        help="Path to configuration file.",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Override output format (terminal, markdown, html, json).",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """Run evaluation pipeline with the specified configuration."""
    path = Path(config_path)

    if not path.exists():
        raise ConfigurationError(
            message=f"Configuration file not found: {config_path}",
            config_path=config_path,
        )

    console.print(f"[bold blue]OpenAgent Eval[/bold blue] v0.1.0")
    console.print(f"[dim]Configuration: {config_path}[/dim]\n")

    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading configuration...", total=None)
        # TODO: Load configuration
        progress.update(task, description="Loading dataset...")
        # TODO: Load dataset
        progress.update(task, description="Running evaluation...")
        # TODO: Run evaluation
        progress.update(task, description="Generating report...")
        # TODO: Generate report

    console.print("\n[green]OK[/green] Evaluation complete!")
    console.print("[dim]Results saved to ./reports/[/dim]")


@app.command()
def report(
    report_id: str = typer.Argument(
        help="Report ID or 'latest' for the most recent report.",
    ),
    output: str = typer.Option(
        "terminal",
        "--output",
        "-o",
        help="Output format (terminal, markdown, html, json).",
    ),
) -> None:
    """View evaluation reports."""
    console.print(f"[bold blue]OpenAgent Eval[/bold blue] - Report Viewer")
    console.print(f"[dim]Report: {report_id}[/dim]\n")

    # TODO: Implement report viewing
    console.print("[yellow]Report viewing not yet implemented.[/yellow]")
    console.print("This will display the evaluation report in the specified format.")


@app.command()
def compare(
    experiment_a: str = typer.Argument(
        help="First experiment ID or path.",
    ),
    experiment_b: str = typer.Argument(
        help="Second experiment ID or path.",
    ),
    metrics: list[str] = typer.Option(
        None,
        "--metrics",
        "-m",
        help="Specific metrics to compare (default: all).",
    ),
) -> None:
    """Compare two evaluation experiments side by side."""
    console.print(f"[bold blue]OpenAgent Eval[/bold blue] - Experiment Comparison")
    console.print(f"[dim]Comparing: {experiment_a} vs {experiment_b}[/dim]\n")

    # TODO: Implement experiment comparison
    console.print("[yellow]Experiment comparison not yet implemented.[/yellow]")
    console.print("This will show a side-by-side comparison of the two experiments.")


@app.command(name="list")
def list_evaluations(
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of evaluations to show.",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Filter by output format.",
    ),
) -> None:
    """List previous evaluation runs."""
    console.print(f"[bold blue]OpenAgent Eval[/bold blue] - Evaluation History\n")

    # TODO: Implement listing evaluations
    table = Table(title="Recent Evaluations")
    table.add_column("ID", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Config", style="yellow")
    table.add_column("Status", style="bold")

    # Placeholder data
    table.add_row("eval_001", "2025-07-08", "config.yaml", "OK Complete")
    table.add_row("eval_002", "2025-07-07", "config_v2.yaml", "OK Complete")
    table.add_row("eval_003", "2025-07-06", "config.yaml", "FAILED Failed")

    console.print(table)
    console.print(f"\n[dim]Showing {limit} of 3 evaluations[/dim]")


@app.command()
def doctor(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information.",
    ),
) -> None:
    """Check environment and dependencies for OpenAgent Eval."""
    console.print(f"[bold blue]OpenAgent Eval[/bold blue] - Environment Check\n")

    table = Table(title="Environment Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row(
        "Python",
        "[green]OK[/green]" if sys.version_info >= (3, 11) else "[red]MISSING[/red]",
        f"v{python_version}",
    )

    # Check dependencies
    dependencies = [
        ("typer", "CLI framework"),
        ("rich", "Terminal UI"),
        ("pydantic", "Data validation"),
        ("yaml", "Configuration"),
        ("loguru", "Logging"),
    ]

    for dep_name, dep_desc in dependencies:
        try:
            __import__(dep_name.replace("-", "_"))
            table.add_row(dep_name, "[green]OK[/green]", dep_desc)
        except ImportError:
            table.add_row(dep_name, "[red]MISSING[/red]", f"{dep_desc} (not installed)")

    console.print(table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    if sys.version_info >= (3, 11):
        console.print("[green]OK[/green] Python version is compatible")
    else:
        console.print("[red]MISSING[/red] Python 3.11+ required")

    console.print("\n[dim]Run 'pip install openagent-eval[all]' to install all dependencies.[/dim]")


DEFAULT_CONFIG_CONTENT = """\
# OpenAgent Eval Configuration
# Documentation: https://github.com/openagenthq/openagent-eval

# Dataset configuration
dataset: data/questions.json

# Retriever configuration
retriever:
  provider: chroma
  settings:
    collection_name: my_docs

# LLM configuration
llm:
  provider: openai
  model: gpt-4o

# Metrics to evaluate
metrics:
  - faithfulness
  - answer_relevancy
  - hallucination
  - latency

# Report configuration
output: terminal
output_dir: ./reports
"""
