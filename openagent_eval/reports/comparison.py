"""Comparison report generator for side-by-side experiment analysis."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport


class ComparisonReportGenerator:
    """Compare two EvaluationReport objects side-by-side.

    Shows absolute and percentage differences for every metric, with
    colour-coding for improvements and regressions.
    """

    name = "comparison"
    description = "Side-by-side experiment comparison"

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        *,
        label_a: str = "Experiment A",
        label_b: str = "Experiment B",
    ) -> str:
        """Generate a Markdown comparison report.

        Args:
            report_a: First (baseline) evaluation report.
            report_b: Second (new) evaluation report.
            label_a: Display label for the baseline.
            label_b: Display label for the new experiment.

        Returns:
            A Markdown string with the comparison.
        """
        sections: list[str] = []

        sections.append(self._header(label_a, label_b))
        sections.append(self._summary_table(report_a, report_b, label_a, label_b))
        sections.append(self._metrics_comparison(report_a, report_b, label_a, label_b))
        sections.append(self._item_comparison(report_a, report_b))

        return "\n\n".join(s for s in sections if s) + "\n"

    def save(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        output_path: Path,
        *,
        label_a: str = "Experiment A",
        label_b: str = "Experiment B",
    ) -> Path:
        """Save the comparison report to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            self.generate(report_a, report_b, label_a=label_a, label_b=label_b),
            encoding="utf-8",
        )
        return output_path

    # ------------------------------------------------------------------ #
    # Section builders                                                    #
    # ------------------------------------------------------------------ #

    def _header(self, label_a: str, label_b: str) -> str:
        """Return the comparison header."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return (
            f"# Experiment Comparison\n\n"
            f"**{label_a}** vs **{label_b}**\n\n"
            f"Generated: {timestamp}"
        )

    def _summary_table(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        label_a: str,
        label_b: str,
    ) -> str:
        """Return a summary comparison table."""
        sa = report_a.summary
        sb = report_b.summary

        total_a = sa.get("total_items", len(report_a.result.results))
        total_b = sb.get("total_items", len(report_b.result.results))
        err_a = sa.get("failed_evaluations", len(report_a.result.errors))
        err_b = sb.get("failed_evaluations", len(report_b.result.errors))

        rate_a = ((total_a - err_a) / total_a * 100) if total_a > 0 else 0.0
        rate_b = ((total_b - err_b) / total_b * 100) if total_b > 0 else 0.0

        return (
            "## Summary\n\n"
            f"| Metric | {label_a} | {label_b} | Delta |\n"
            f"|--------|----------|----------|-------|\n"
            f"| Total Items | {total_a} | {total_b} | {self._delta_str(total_b, total_a)} |\n"
            f"| Successful | {total_a - err_a} | {total_b - err_b} | "
            f"{self._delta_str(total_b - err_b, total_a - err_a)} |\n"
            f"| Failed | {err_a} | {err_b} | {self._delta_str(err_b, err_a)} |\n"
            f"| Success Rate | {rate_a:.1f}% | {rate_b:.1f}% | "
            f"{self._pct_delta(rate_b, rate_a)}% |"
        )

    def _metrics_comparison(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        label_a: str,
        label_b: str,
    ) -> str:
        """Return a metrics-by-metric comparison table."""
        metrics_a = self._get_metrics(report_a)
        metrics_b = self._get_metrics(report_b)

        all_keys = sorted(set(metrics_a) | set(metrics_b))
        if not all_keys:
            return ""

        lines = [
            "## Metrics Comparison",
            "",
            f"| Metric | {label_a} | {label_b} | Delta | Δ% |",
            "|--------|----------|----------|-------|----|",
        ]

        for key in all_keys:
            val_a = metrics_a.get(key, 0.0)
            val_b = metrics_b.get(key, 0.0)
            delta = val_b - val_a
            pct = ((delta / val_a) * 100) if val_a != 0 else 0.0
            indicator = self._indicator(delta)
            lines.append(
                f"| {key} | {val_a:.4f} | {val_b:.4f} | "
                f"{self._signed(delta)} | {self._signed(pct)}% {indicator} |"
            )

        return "\n".join(lines)

    def _item_comparison(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
    ) -> str:
        """Return a per-item comparison (questions in both reports)."""
        results_a = {r.question: r for r in report_a.result.results}
        results_b = {r.question: r for r in report_b.result.results}

        shared = set(results_a) & set(results_b)
        if not shared:
            return ""

        lines = ["## Per-Item Comparison", ""]

        for question in sorted(shared):
            ra = results_a[question]
            rb = results_b[question]

            lines.append(f"### {question}")
            lines.append("")
            lines.append("| Metric | A | B | Δ |")
            lines.append("|--------|---|---|---|")

            all_metrics = sorted(set(ra.metrics) | set(rb.metrics))
            for m in all_metrics:
                va = ra.metrics.get(m, 0.0)
                vb = rb.metrics.get(m, 0.0)
                delta = vb - va
                indicator = self._indicator(delta)
                lines.append(
                    f"| {m} | {va:.4f} | {vb:.4f} | "
                    f"{self._signed(delta)} {indicator} |"
                )

            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Utility helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_metrics(report: EvaluationReport) -> dict[str, float]:
        """Extract metric averages from a report."""
        metrics = report.summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})
        return dict(metrics) if isinstance(metrics, dict) else {}

    @staticmethod
    def _delta_str(new: float, old: float) -> str:
        """Format a delta value with sign."""
        d = new - old
        if d > 0:
            return f"+{d:.2f}"
        return f"{d:.2f}"

    @staticmethod
    def _signed(value: float) -> str:
        """Format with explicit sign."""
        if value > 0:
            return f"+{value:.4f}"
        return f"{value:.4f}"

    @staticmethod
    def _pct_delta(new_pct: float, old_pct: float) -> str:
        """Format percentage delta."""
        d = new_pct - old_pct
        if d > 0:
            return f"+{d:.2f}"
        return f"{d:.2f}"

    @staticmethod
    def _indicator(delta: float) -> str:
        """Return an emoji indicator for a delta value."""
        if delta > 0:
            return ":green_circle:"
        if delta < 0:
            return ":red_circle:"
        return ":white_circle:"
