"""Main CLI entry point for OpenAgent Eval."""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from openagent_eval import __version__
from openagent_eval.config.loader import load_config
from openagent_eval.config.models import OutputFormat
from openagent_eval.core.engine import Engine
from openagent_eval.datasets.factory import load_dataset
from openagent_eval.exceptions import ConfigurationError
from openagent_eval.exceptions.cli import CommandError
from openagent_eval.reports.comparison import ComparisonReportGenerator
from openagent_eval.reports.html import HTMLReportGenerator
from openagent_eval.reports.json_report import JSONReportGenerator
from openagent_eval.reports.manager import ReportManager
from openagent_eval.reports.markdown import MarkdownReportGenerator
from openagent_eval.reports.terminal import TerminalReportGenerator

app = typer.Typer(
    name="oaeval",
    help="Open-source CLI framework for evaluating RAG systems and AI Agents.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()

# ------------------------------------------------------------------ #
# Constants                                                           #
# ------------------------------------------------------------------ #

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

REPORT_GENERATORS: dict[str, type] = {
    "terminal": TerminalReportGenerator,
    "markdown": MarkdownReportGenerator,
    "html": HTMLReportGenerator,
    "json": JSONReportGenerator,
}

DEFAULT_OUTPUT_DIR = Path("./reports")

# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #


def _get_report_generator(format_name: str) -> Any:
    """Get a report generator instance by format name.

    Args:
        format_name: The output format identifier.

    Returns:
        An instance of the appropriate ReportGenerator.

    Raises:
        CommandError: If the format is not supported.
    """
    generator_cls = REPORT_GENERATORS.get(format_name)
    if generator_cls is None:
        supported = ", ".join(REPORT_GENERATORS.keys())
        raise CommandError(
            message=f"Unsupported output format: '{format_name}'. Supported formats: {supported}",
            command="report",
        )
    return generator_cls()


def _resolve_report_id(
    report_id: str,
    output_dir: Path,
    manager: ReportManager,
) -> dict[str, Any]:
    """Resolve a report ID or 'latest' keyword to a report payload.

    Args:
        report_id: The report identifier or 'latest'.
        output_dir: Directory where reports are stored.
        manager: ReportManager instance.

    Returns:
        The deserialized report payload.

    Raises:
        CommandError: If the report cannot be found.
    """
    try:
        if report_id.lower() == "latest":
            return manager.get_latest_report(output_dir)
        return manager.load_report(report_id, output_dir)
    except FileNotFoundError as e:
        raise CommandError(
            message=f"Report not found: {report_id}",
            command="report",
        ) from e


def _load_config_from_path(config_path: str) -> Any:
    """Load configuration from a YAML file path.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        The validated configuration.

    Raises:
        CommandError: If loading fails.
    """
    try:
        return load_config(config_path)
    except ConfigurationError as e:
        raise CommandError(message=str(e), command="run") from e


def _apply_output_override(config: Any, output: str | None) -> None:
    """Apply output format override to config if specified.

    Args:
        config: The loaded configuration.
        output: Optional output format string.

    Raises:
        CommandError: If the format is not supported.
    """
    if output:
        try:
            format_enum = OutputFormat(output)
            config.report.output = format_enum
        except ValueError as e:
            supported = ", ".join(f.value for f in OutputFormat)
            raise CommandError(
                message=f"Unsupported output format: '{output}'. Supported: {supported}",
                command="run",
            ) from e


def _load_dataset_for_run(config: Any) -> list[dict[str, Any]]:
    """Load dataset from configuration.

    Args:
        config: The loaded configuration.

    Returns:
        List of dataset items.

    Raises:
        CommandError: If dataset loading fails.
    """
    try:
        return load_dataset(config.dataset)
    except Exception as e:
        raise CommandError(
            message=f"Failed to load dataset: {e}", command="run"
        ) from e


def _display_run_result(
    report: Any,
    format_name: str,
    report_path: Path,
    output_dir: Path,
    verbose: bool,
) -> None:
    """Display the evaluation run result.

    Args:
        report: The evaluation report.
        format_name: The output format used.
        report_path: Path where the report was saved.
        output_dir: The output directory.
        verbose: Whether verbose output is enabled.
    """
    console.print("\n[green]OK[/green] Evaluation complete!")

    # Show summary
    if hasattr(report, "summary"):
        summary = report.summary
        total = summary.get("total_items", summary.get("total", 0))
        errors = summary.get("failed_evaluations", summary.get("errors", 0))
        console.print(f"[dim]Items: {total} | Errors: {errors}[/dim]")

    # Show report location
    console.print(f"[dim]Report saved to: {report_path}[/dim]")

    # Show metrics summary if available
    if hasattr(report, "result") and hasattr(report.result, "summary"):
        metrics = report.result.summary.get("metrics", {})
        if metrics:
            console.print("\n[bold]Metrics Summary:[/bold]")
            for metric_name, score in metrics.items():
                console.print(f"  {metric_name}: {score:.4f}")


def _execute_evaluation(config: Any, dataset_items: list[dict[str, Any]]) -> Any:
    """Execute the evaluation engine.

    Args:
        config: The loaded configuration.
        dataset_items: List of dataset items.

    Returns:
        The evaluation report.

    Raises:
        CommandError: If evaluation fails.
    """
    engine = Engine(config)
    try:
        return asyncio.run(engine.run(dataset_items))
    except Exception as e:
        raise CommandError(
            message=f"Evaluation failed: {e}", command="run"
        ) from e
    finally:
        engine.shutdown()


def _display_report_list(
    reports: list[dict[str, str]],
    limit: int,
    output_filter: str | None,
    output_dir: Path,
    manager: ReportManager,
) -> None:
    """Display a table of evaluation reports.

    Args:
        reports: List of report metadata dicts.
        limit: Maximum number of reports to show.
        output_filter: Optional format filter.
        output_dir: Directory where reports are stored.
        manager: ReportManager instance.
    """
    if not reports:
        console.print("[yellow]No evaluations found.[/yellow]")
        return

    # Optionally filter by output format
    if output_filter:
        filtered: list[dict[str, str]] = []
        for r in reports:
            try:
                data = manager.load_report(r["report_id"], output_dir)
                report_format = (
                    data.get("config", {}).get("report", {}).get("output", "terminal")
                )
                if report_format == output_filter:
                    filtered.append(r)
            except (FileNotFoundError, KeyError):
                continue
        reports = filtered

    # Apply limit
    reports = reports[:limit]

    table = Table(title="Recent Evaluations")
    table.add_column("ID", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Config", style="yellow")
    table.add_column("Status", style="bold")

    for r in reports:
        report_id = r["report_id"]
        created_at = r.get("created_at", "unknown")

        # Try to extract config and status from the report
        config_name = "unknown"
        status = "OK"
        try:
            data = manager.load_report(report_id, output_dir)
            config_name = data.get("config", {}).get("dataset", {}).get("path", "unknown")
            errors = data.get("errors", [])
            status = "[green]OK[/green]" if not errors else "[red]FAILED[/red]"
        except (FileNotFoundError, KeyError):
            status = "[yellow]UNKNOWN[/yellow]"

        # Format the date
        if created_at and "T" in created_at:
            created_at = created_at.split("T")[0]

        table.add_row(report_id, created_at, config_name, status)

    console.print(table)
    console.print(f"\n[dim]Showing {len(reports)} of {len(reports)} evaluations[/dim]")


# ------------------------------------------------------------------ #
# Version callback                                                    #
# ------------------------------------------------------------------ #


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


# ------------------------------------------------------------------ #
# Command: init                                                       #
# ------------------------------------------------------------------ #


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

    if path.exists() and not force and not Confirm.ask(f"Configuration file '{config_path}' already exists. Overwrite?"):
        console.print("[yellow]Aborted.[/yellow]")
        raise typer.Exit()

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        console.print(f"[green]OK[/green] Configuration created: {config_path}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  1. Edit the configuration file")
        console.print("  2. Run [bold]oaeval run[/bold] to start evaluation")
    except OSError as e:
        raise ConfigurationError(
            message=f"Failed to create configuration: {e}",
            config_path=config_path,
        ) from e


# ------------------------------------------------------------------ #
# Command: run                                                        #
# ------------------------------------------------------------------ #


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

    console.print(f"[bold blue]OpenAgent Eval[/bold blue] v{__version__}")
    console.print(f"[dim]Configuration: {config_path}[/dim]\n")

    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Load configuration
        task = progress.add_task("Loading configuration...", total=None)
        config = _load_config_from_path(config_path)
        _apply_output_override(config, output)

        # Step 2: Load dataset
        progress.update(task, description="Loading dataset...")
        dataset_items = _load_dataset_for_run(config)

        # Step 3: Run evaluation
        progress.update(task, description="Running evaluation...")
        report = _execute_evaluation(config, dataset_items)

        # Step 4: Save report
        progress.update(task, description="Generating report...")
        format_name = config.report.output.value
        manager = ReportManager()
        output_dir = Path(config.report.output_dir)
        report_path = manager.save_report(report, output_dir)

        # Step 5: Display summary
        progress.update(task, description="Complete!", completed=True)

    _display_run_result(report, format_name, report_path, output_dir, verbose)


# ------------------------------------------------------------------ #
# Command: report                                                     #
# ------------------------------------------------------------------ #


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
    output_dir: str = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Directory where reports are stored (default: ./reports).",
    ),
) -> None:
    """View evaluation reports."""
    console.print("[bold blue]OpenAgent Eval[/bold blue] - Report Viewer")
    console.print(f"[dim]Report: {report_id}[/dim]\n")

    manager = ReportManager()
    reports_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    try:
        data = _resolve_report_id(report_id, reports_dir, manager)
    except CommandError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(code=e.exit_code) from None

    # Reconstruct the EvaluationReport from saved data
    evaluation_report = manager.reconstruct(data)

    # Render in requested format
    try:
        generator = _get_report_generator(output)
    except CommandError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(code=e.exit_code) from None

    if output == "terminal":
        gen = TerminalReportGenerator()
        gen._render(evaluation_report, console, verbose=False)
    else:
        report_content = generator.generate(evaluation_report)
        console.print(report_content)

    console.print(f"\n[dim]Report ID: {data.get('report_id', 'unknown')}[/dim]")


# ------------------------------------------------------------------ #
# Command: compare                                                    #
# ------------------------------------------------------------------ #


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
    output_dir: str = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Directory where reports are stored (default: ./reports).",
    ),
) -> None:
    """Compare two evaluation experiments side by side."""
    console.print("[bold blue]OpenAgent Eval[/bold blue] - Experiment Comparison")
    console.print(f"[dim]Comparing: {experiment_a} vs {experiment_b}[/dim]\n")

    manager = ReportManager()
    reports_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    # Load both reports
    try:
        data_a = _resolve_report_id(experiment_a, reports_dir, manager)
    except CommandError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(code=e.exit_code) from None

    try:
        data_b = _resolve_report_id(experiment_b, reports_dir, manager)
    except CommandError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        raise typer.Exit(code=e.exit_code) from None

    # Reconstruct EvaluationReports
    report_a = manager.reconstruct(data_a)
    report_b = manager.reconstruct(data_b)

    # Generate comparison
    comparator = ComparisonReportGenerator()
    comparison_output = comparator.generate(
        report_a,
        report_b,
        label_a=experiment_a,
        label_b=experiment_b,
    )

    # Filter metrics if specified
    if metrics:
        lines = comparison_output.split("\n")
        filtered_lines: list[str] = []

        for line in lines:
            # Only filter metric-specific rows in tables
            if line.startswith("|") and not line.startswith("|---"):
                row_parts = [p.strip() for p in line.split("|") if p.strip()]
                if row_parts and row_parts[0] not in metrics and row_parts[0] != "Metric":
                    continue
            filtered_lines.append(line)

        comparison_output = "\n".join(filtered_lines)

    console.print(comparison_output)


# ------------------------------------------------------------------ #
# Command: list                                                       #
# ------------------------------------------------------------------ #


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
    output_dir: str = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Directory where reports are stored (default: ./reports).",
    ),
) -> None:
    """List previous evaluation runs."""
    console.print("[bold blue]OpenAgent Eval[/bold blue] - Evaluation History\n")

    manager = ReportManager()
    reports_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    try:
        reports = manager.list_reports(reports_dir)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to list reports: {e}")
        raise typer.Exit(code=1) from e

    _display_report_list(reports, limit, output, reports_dir, manager)


# ------------------------------------------------------------------ #
# Command: doctor                                                     #
# ------------------------------------------------------------------ #


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
    console.print("[bold blue]OpenAgent Eval[/bold blue] - Environment Check\n")

    table = Table(title="Environment Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 11)
    table.add_row(
        "Python",
        "[green]OK[/green]" if python_ok else "[red]MISSING[/red]",
        f"v{python_version}" + ("" if python_ok else " (3.11+ required)"),
    )

    # Check dependencies
    dependencies = [
        ("typer", "CLI framework"),
        ("rich", "Terminal UI"),
        ("pydantic", "Data validation"),
        ("yaml", "Configuration"),
        ("loguru", "Logging"),
        ("jinja2", "HTML templates"),
    ]

    for dep_name, dep_desc in dependencies:
        try:
            importlib.import_module(dep_name.replace("-", "_"))
            table.add_row(dep_name, "[green]OK[/green]", dep_desc)
        except ImportError:
            table.add_row(dep_name, "[red]MISSING[/red]", f"{dep_desc} (not installed)")

    console.print(table)

    # API key checks
    console.print()
    key_table = Table(title="API Key Availability")
    key_table.add_column("Provider", style="cyan")
    key_table.add_column("Environment Variable", style="yellow")
    key_table.add_column("Status", style="bold")

    api_keys = [
        ("OpenAI", "OPENAI_API_KEY"),
        ("Gemini", "GEMINI_API_KEY"),
        ("Anthropic", "ANTHROPIC_API_KEY"),
        ("Groq", "GROQ_API_KEY"),
    ]

    available_providers: list[str] = []
    for provider_name, env_var in api_keys:
        key_value = os.environ.get(env_var)
        if key_value:
            key_table.add_row(
                provider_name,
                env_var,
                "[green]Available[/green]",
            )
            available_providers.append(provider_name)
        else:
            key_table.add_row(
                provider_name,
                env_var,
                "[dim]Not set[/dim]",
            )

    console.print(key_table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    if python_ok:
        console.print("[green]OK[/green] Python version is compatible")
    else:
        console.print("[red]MISSING[/red] Python 3.11+ required")

    if available_providers:
        console.print(
            f"[green]OK[/green] Available providers: {', '.join(available_providers)}"
        )
    else:
        console.print("[yellow]WARNING[/yellow] No API keys configured")

    if verbose:
        console.print(f"\n[dim]Python: {sys.executable}[/dim]")
        console.print(f"[dim]Version: {__version__}[/dim]")

    console.print("\n[dim]Run 'pip install openagent-eval[all]' to install all dependencies.[/dim]")
