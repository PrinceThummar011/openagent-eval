"""Audit command for corpus health checking."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from openagent_eval import __version__
from openagent_eval.cli.context import get_context
from openagent_eval.corpus.auditor import CorpusAuditor
from openagent_eval.corpus.models import AuditReport, IssueSeverity
from openagent_eval.exceptions.corpus import CorpusAuditError, CorpusNotFoundError

console = Console()


def audit_command(
    corpus_path: str = typer.Argument(
        ...,
        help="Path to the corpus directory or file to audit.",
    ),
    checks: str | None = typer.Option(
        None,
        "--checks",
        "-c",
        help="Comma-separated checks to perform (contradiction, staleness, duplicate, coverage).",
    ),
    staleness_days: int = typer.Option(
        365,
        "--staleness-days",
        help="Days threshold for staleness detection.",
    ),
    similarity_threshold: float = typer.Option(
        0.92,
        "--similarity-threshold",
        help="Similarity threshold for duplicate detection (0.0-1.0).",
    ),
    max_documents: int = typer.Option(
        1000,
        "--max-documents",
        help="Maximum documents to audit.",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output format (json, or leave empty for terminal).",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """Audit corpus health before connecting to RAG.

    Scans the knowledge base for contradictions, staleness, duplicates,
    and thematic coverage gaps. Run this BEFORE connecting to RAG.

    Example:

        oaeval audit ./knowledge_base/

        oaeval audit ./docs/ --checks contradiction,staleness

        oaeval audit ./kb/ --staleness-days 180
    """
    ctx = get_context()

    if verbose:
        ctx.verbose = True

    if not ctx.quiet:
        console.print(f"[bold blue]OpenAgent Eval[/bold blue] v{__version__}")
        console.print(f"[dim]Corpus: {corpus_path}[/dim]\n")

    # Validate path
    path = Path(corpus_path)
    if not path.exists():
        console.print(f"[red]Error:[/red] Path does not exist: {corpus_path}")
        raise typer.Exit(code=2)

    # Parse checks
    check_list = None
    if checks:
        check_list = [c.strip() for c in checks.split(",") if c.strip()]
        valid_checks = {"contradiction", "staleness", "duplicate", "coverage"}
        for check in check_list:
            if check not in valid_checks:
                console.print(f"[red]Error:[/red] Unknown check: {check}")
                console.print(f"[dim]Valid checks: {', '.join(sorted(valid_checks))}[/dim]")
                raise typer.Exit(code=2)

    # Create auditor
    auditor = CorpusAuditor(
        checks=check_list,
        staleness_days=staleness_days,
        similarity_threshold=similarity_threshold,
        max_documents=max_documents,
    )

    # Run audit with progress
    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        disable=ctx.quiet,
    ) as progress:
        task = progress.add_task("Loading corpus...", total=None)

        progress.update(task, description="Scanning documents...")
        try:
            report = asyncio.run(auditor.audit(corpus_path))
        except CorpusNotFoundError as e:
            console.print(f"[red]Error:[/red] {e.message}")
            raise typer.Exit(code=2) from e
        except CorpusAuditError as e:
            console.print(f"[red]Error:[/red] {e.message}")
            raise typer.Exit(code=3) from e

        progress.update(task, description="Audit complete!", completed=True)

    elapsed = time.time() - start_time

    # Output results
    if output == "json":
        _output_json(report, elapsed)
    else:
        _display_report(report, elapsed, verbose)


def _display_report(report: AuditReport, elapsed: float, verbose: bool) -> None:
    """Display the audit report in the terminal.

    Args:
        report: The audit report.
        elapsed: Time elapsed in seconds.
        verbose: Whether to show verbose output.
    """
    # Health score panel
    score_color = "green" if report.health_score >= 0.8 else "yellow" if report.health_score >= 0.5 else "red"
    score_label = "Healthy" if report.health_score >= 0.8 else "Needs Attention" if report.health_score >= 0.5 else "Unhealthy"

    console.print()
    console.print(
        Panel(
            f"[{score_color} bold]{report.health_score:.1%}[/{score_color} bold] — {score_label}",
            title="[bold]Corpus Health Score[/bold]",
            border_style=score_color,
        )
    )

    # Summary
    console.print(f"\n[bold]Summary:[/bold] {report.summary}")

    # Issues table
    if report.issues:
        table = Table(title="Issues Found", show_lines=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Type", width=15)
        table.add_column("Title", min_width=30)
        table.add_column("Documents", width=20)

        severity_styles = {
            IssueSeverity.CRITICAL: "red bold",
            IssueSeverity.HIGH: "red",
            IssueSeverity.MEDIUM: "yellow",
            IssueSeverity.LOW: "dim",
        }

        for issue in sorted(report.issues, key=lambda i: list(IssueSeverity).index(i.severity)):
            style = severity_styles.get(issue.severity, "")
            docs = ", ".join(issue.document_ids[:3])
            if len(issue.document_ids) > 3:
                docs += f" (+{len(issue.document_ids) - 3} more)"

            table.add_row(
                f"[{style}]{issue.severity.value.upper()}[/{style}]",
                issue.issue_type.value,
                issue.title,
                docs,
            )

        console.print()
        console.print(table)
    else:
        console.print("\n[green]No issues found![/green]")

    # Verbose details
    if verbose:
        console.print(f"\n[dim]Checks performed: {', '.join(report.checks_performed)}[/dim]")
        console.print(f"[dim]Documents analyzed: {report.total_documents}[/dim]")
        console.print(f"[dim]Time elapsed: {elapsed:.1f}s[/dim]")

        # Group by type
        by_type = report.issues_by_type
        if by_type:
            console.print("\n[bold]Issues by Type:[/bold]")
            for issue_type, issues in by_type.items():
                console.print(f"  {issue_type.value}: {len(issues)}")


def _output_json(report: AuditReport, elapsed: float) -> None:
    """Output the report as JSON.

    Args:
        report: The audit report.
        elapsed: Time elapsed in seconds.
    """
    import json

    result = {
        "status": "success",
        "health_score": report.health_score,
        "total_documents": report.total_documents,
        "issues_count": len(report.issues),
        "issues": [
            {
                "type": issue.issue_type.value,
                "severity": issue.severity.value,
                "title": issue.title,
                "description": issue.description,
                "document_ids": issue.document_ids,
                "metadata": issue.metadata,
            }
            for issue in report.issues
        ],
        "checks_performed": report.checks_performed,
        "summary": report.summary,
        "elapsed_seconds": round(elapsed, 2),
    }

    console.print(json.dumps(result, indent=2))
