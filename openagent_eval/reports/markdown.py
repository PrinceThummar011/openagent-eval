"""Markdown report generator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from openagent_eval.reports.base import ReportGenerator

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport


class MarkdownReportGenerator(ReportGenerator):
    """Generate a clean Markdown report with headers, tables, and lists."""

    name = "markdown"
    description = "Markdown report for documentation and sharing"

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(self, report: EvaluationReport) -> str:
        """Render the report as a Markdown string."""
        sections: list[str] = []

        sections.append(self._header(report))
        sections.append(self._summary_section(report))
        sections.append(self._metrics_section(report))
        sections.append(self._results_section(report))
        sections.append(self._failures_section(report))
        sections.append(self._footer(report))

        return "\n\n".join(s for s in sections if s) + "\n"

    def save(self, report: EvaluationReport, output_path: Path) -> Path:
        """Generate and save the Markdown report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.generate(report), encoding="utf-8")
        return output_path

    # ------------------------------------------------------------------ #
    # Section builders                                                    #
    # ------------------------------------------------------------------ #

    def _header(self, report: EvaluationReport) -> str:
        """Return the report header."""
        title = "# OpenAgent Eval – Evaluation Report"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        meta = f"Generated: {timestamp}"
        return f"{title}\n\n{meta}"

    def _summary_section(self, report: EvaluationReport) -> str:
        """Return the summary section."""
        summary = report.summary
        total = summary.get("total_items", len(report.result.results))
        errors = summary.get("failed_evaluations", len(report.result.errors))
        success_rate = ((total - errors) / total * 100) if total > 0 else 0.0

        lines = [
            "## Summary",
            "",
            f"| Item | Value |",
            f"|------|-------|",
            f"| Total Items | {total} |",
            f"| Successful | {total - errors} |",
            f"| Failed | {errors} |",
            f"| Success Rate | {success_rate:.1f}% |",
        ]

        # Config summary
        cfg = report.config
        lines += [
            "",
            f"- **LLM Provider:** `{cfg.llm.provider}`",
            f"- **Model:** `{cfg.llm.model}`",
            f"- **Dataset:** `{cfg.dataset.path}`",
        ]

        return "\n".join(lines)

    def _metrics_section(self, report: EvaluationReport) -> str:
        """Return the metrics section."""
        metrics = report.summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})
        if not metrics:
            return "## Metrics\n\n_No metrics available._"

        lines = [
            "## Metrics",
            "",
            "| Metric | Average |",
            "|--------|---------|",
        ]
        for name, value in metrics.items():
            lines.append(f"| {name} | {value:.4f} |")

        return "\n".join(lines)

    def _results_section(self, report: EvaluationReport) -> str:
        """Return the detailed results section."""
        results = report.result.results
        if not results:
            return "## Results\n\n_No results available._"

        lines = [
            "## Results",
        ]

        for idx, item in enumerate(results, 1):
            lines.append(f"\n### Item {idx}")
            lines.append("")
            lines.append(f"**Question:** {item.question}")
            lines.append("")
            lines.append(f"**Answer:** {item.answer or '_(empty)_'}")
            lines.append("")

            if item.ground_truth:
                lines.append(f"**Ground Truth:** {item.ground_truth}")
                lines.append("")

            if item.metrics:
                lines.append("| Metric | Score |")
                lines.append("|--------|-------|")
                for name, score in item.metrics.items():
                    lines.append(f"| {name} | {score:.4f} |")
                lines.append("")

        return "\n".join(lines)

    def _failures_section(self, report: EvaluationReport) -> str:
        """Return the failure analysis section."""
        errors = report.result.errors
        if not errors:
            return ""

        lines = [
            "## Failures",
            "",
            f"_ {len(errors)} error(s) encountered during evaluation._",
            "",
        ]

        for idx, err in enumerate(errors, 1):
            error_type = err.get("type", "Unknown")
            error_msg = err.get("error", "No message")
            lines.append(f"{idx}. **{error_type}**: {error_msg}")

        return "\n".join(lines)

    def _footer(self, report: EvaluationReport) -> str:
        """Return the report footer."""
        meta = report.metadata
        version = meta.get("version", "unknown")
        return f"---\n\n_OpenAgent Eval v{version}_"
