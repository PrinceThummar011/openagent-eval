"""JSON report generator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from openagent_eval.reports.base import ReportGenerator

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport


class JSONReportGenerator(ReportGenerator):
    """Serialize an EvaluationReport to structured JSON."""

    name = "json"
    description = "Machine-readable JSON report"

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(self, report: EvaluationReport) -> str:
        """Render the report as a JSON string."""
        payload = self._to_dict(report)
        return json.dumps(payload, indent=2, default=str)

    def save(self, report: EvaluationReport, output_path: Path) -> Path:
        """Generate and save the JSON report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.generate(report), encoding="utf-8")
        return output_path

    # ------------------------------------------------------------------ #
    # Serialization helpers                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_dict(report: EvaluationReport) -> dict[str, Any]:
        """Convert the report to a JSON-safe dictionary."""
        summary = report.summary
        total = summary.get("total_items", len(report.result.results))
        errors = summary.get("failed_evaluations", len(report.result.errors))

        metrics = summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})

        return {
            "metadata": {
                "version": report.metadata.get("version", "unknown"),
                "engine": report.metadata.get("engine", "openagent-eval"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "config": {
                "llm": {
                    "provider": report.config.llm.provider,
                    "model": report.config.llm.model,
                    "temperature": report.config.llm.temperature,
                },
                "dataset": {
                    "path": report.config.dataset.path,
                },
            },
            "summary": {
                "total_items": total,
                "successful_evaluations": total - errors,
                "failed_evaluations": errors,
                "success_rate": ((total - errors) / total * 100) if total > 0 else 0.0,
                "metrics_summary": metrics,
            },
            "results": [
                {
                    "question": item.question,
                    "answer": item.answer,
                    "ground_truth": item.ground_truth,
                    "contexts": item.contexts,
                    "metrics": item.metrics,
                    "metadata": item.metadata,
                }
                for item in report.result.results
            ],
            "errors": report.result.errors,
        }
