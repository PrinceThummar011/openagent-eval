"""Terminal report generator using Rich."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from openagent_eval.reports.base import ReportGenerator

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport


class TerminalReportGenerator(ReportGenerator):
    """Generate beautiful terminal output using Rich.

    Produces a human-friendly summary with coloured metrics, summary
    statistics, and optional per-item detail.
    """

    name = "terminal"
    description = "Terminal report with Rich formatting"

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(self, report: EvaluationReport) -> str:
        """Render the report as a plain-text string.

        The output mirrors the Rich-rendered panels but strips ANSI escape
        codes so the result can be saved or piped without a TTY.
        """
        console = Console(file=None, force_terminal=True, record=True)
        self._render(report, console, verbose=False)
        return console.export_text(styles=False)

    def save(self, report: EvaluationReport, output_path: Path) -> Path:
        """Save the terminal report to a file.

        Because terminal output is ANSI-coloured, we write using
        ``record=True`` / ``export_text`` so the file is always
        plain-text.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.generate(report), encoding="utf-8")
        return output_path

    # ------------------------------------------------------------------ #
    # Internal rendering helpers                                          #
    # ------------------------------------------------------------------ #

    def _render(
        self,
        report: EvaluationReport,
        console: Console,
        *,
        verbose: bool = False,
    ) -> None:
        """Render the full report to the given Rich console."""
        console.print()
        console.print(
            Panel(
                self._build_summary_text(report),
                title="[bold cyan]OpenAgent Eval – Summary[/]",
                border_style="cyan",
            )
        )
        console.print()

        metrics_table = self._build_metrics_table(report)
        if metrics_table:
            console.print(metrics_table)
            console.print()

        if verbose:
            results_table = self._build_results_table(report)
            if results_table:
                console.print(results_table)

    # ------------------------------------------------------------------ #
    # Summary                                                             #
    # ------------------------------------------------------------------ #

    def _build_summary_text(self, report: EvaluationReport) -> Text:
        """Build summary statistics as Rich Text."""
        text = Text()
        summary = report.summary

        total = summary.get("total_items", len(report.result.results))
        errors = summary.get("failed_evaluations", len(report.result.errors))
        success_rate = (
            ((total - errors) / total * 100) if total > 0 else 0.0
        )

        text.append(f"Total Items:      {total}\n", style="bold")
        text.append(f"Successful:       {total - errors}\n", style="green")
        text.append(f"Failed:           {errors}\n", style="red" if errors else "dim")
        text.append(f"Success Rate:     {success_rate:.1f}%\n", style="bold")

        # Metrics averages
        metrics = summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})
        if metrics:
            text.append("\n")
            text.append("Metrics Averages:\n", style="bold yellow")
            for name, value in metrics.items():
                text.append(f"  {name}: {value:.4f}\n", style="dim")

        return text

    # ------------------------------------------------------------------ #
    # Metrics table                                                       #
    # ------------------------------------------------------------------ #

    def _build_metrics_table(self, report: EvaluationReport) -> Table | None:
        """Build a Rich table of metric averages."""
        metrics = report.summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})
        if not metrics:
            return None

        table = Table(title="Metrics Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Average", justify="right", style="green")

        for name, value in metrics.items():
            table.add_row(name, f"{value:.4f}")

        return table

    # ------------------------------------------------------------------ #
    # Per-item results table                                              #
    # ------------------------------------------------------------------ #

    def _build_results_table(self, report: EvaluationReport) -> Table | None:
        """Build a Rich table with per-item results."""
        results = report.result.results
        if not results:
            return None

        table = Table(title="Item Results", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Question", max_width=50)
        table.add_column("Metrics")

        for idx, item in enumerate(results, 1):
            metrics_str = ", ".join(
                f"{k}={v:.2f}" for k, v in item.metrics.items()
            )
            table.add_row(
                str(idx),
                item.question[:50],
                metrics_str or "[dim]—[/]",
            )

        return table


def render_to_console(report: EvaluationReport, *, verbose: bool = False) -> None:
    """Render a report directly to stdout via Rich.

    This is a convenience function for the CLI layer.
    """
    console = Console()
    gen = TerminalReportGenerator()
    gen._render(report, console, verbose=verbose)
