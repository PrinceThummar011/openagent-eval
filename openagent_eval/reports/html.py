"""HTML report generator using Jinja2."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from openagent_eval.reports.base import ReportGenerator

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport

# ------------------------------------------------------------------ #
# Default Jinja2 template                                              #
# ------------------------------------------------------------------ #

_HTML_TEMPLATE = Template(
    """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenAgent Eval – Evaluation Report</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   "Helvetica Neue", Arial, sans-serif;
      background: #f5f7fa;
      color: #1a1a1a;
      line-height: 1.6;
      padding: 2rem;
    }
    .container { max-width: 960px; margin: 0 auto; }
    h1 { font-size: 1.8rem; margin-bottom: .25rem; }
    .timestamp { color: #6b7280; font-size: .85rem; margin-bottom: 1.5rem; }
    .card {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,.08);
      padding: 1.5rem;
      margin-bottom: 1.25rem;
    }
    .card h2 { font-size: 1.15rem; margin-bottom: .75rem; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: .5rem .75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }
    th { background: #f9fafb; font-weight: 600; }
    .badge {
      display: inline-block;
      padding: .15rem .5rem;
      border-radius: 4px;
      font-size: .82rem;
      font-weight: 600;
    }
    .badge-green  { background: #dcfce7; color: #166534; }
    .badge-red    { background: #fee2e2; color: #991b1b; }
    .badge-yellow { background: #fef9c3; color: #854d0e; }
    .badge-blue   { background: #dbeafe; color: #1e40af; }
    .item-block { margin-bottom: 1rem; padding-bottom: 1rem;
                  border-bottom: 1px dashed #e5e7eb; }
    .item-block:last-child { border-bottom: none; }
    .item-block h3 { font-size: 1rem; margin-bottom: .4rem; }
    .dim { color: #6b7280; }
    .footer { text-align: center; color: #9ca3af; font-size: .8rem; margin-top: 2rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>OpenAgent Eval – Evaluation Report</h1>
    <p class="timestamp">Generated: {{ timestamp }}</p>

    <!-- Summary -->
    <div class="card">
      <h2>Summary</h2>
      <table>
        <tr><th>Item</th><th>Value</th></tr>
        <tr><td>Total Items</td><td>{{ total }}</td></tr>
        <tr><td>Successful</td><td><span class="badge badge-green">{{ total - errors }}</span></td></tr>
        <tr><td>Failed</td><td><span class="badge badge-red">{{ errors }}</span></td></tr>
        <tr><td>Success Rate</td><td><span class="badge badge-blue">{{ "%.1f"|format(success_rate) }}%</span></td></tr>
      </table>
      <p class="dim" style="margin-top:.75rem;">
        LLM: <strong>{{ llm_provider }}</strong> / <strong>{{ model }}</strong>
        &mdash; Dataset: <strong>{{ dataset_path }}</strong>
      </p>
    </div>

    <!-- Metrics -->
    {% if metrics %}
    <div class="card">
      <h2>Metrics</h2>
      <table>
        <tr><th>Metric</th><th style="text-align:right;">Average</th></tr>
        {% for name, value in metrics.items() %}
        <tr>
          <td>{{ name }}</td>
          <td style="text-align:right;">
            <span class="badge badge-yellow">{{ "%.4f"|format(value) }}</span>
          </td>
        </tr>
        {% endfor %}
      </table>
    </div>
    {% endif %}

    <!-- Results -->
    {% if results %}
    <div class="card">
      <h2>Results</h2>
      {% for item in results %}
      <div class="item-block">
        <h3>Item {{ loop.index }}</h3>
        <p><strong>Question:</strong> {{ item.question }}</p>
        <p><strong>Answer:</strong> {{ item.answer or "_(empty)_" }}</p>
        {% if item.ground_truth %}
        <p><strong>Ground Truth:</strong> {{ item.ground_truth }}</p>
        {% endif %}
        {% if item.metrics %}
        <table style="margin-top:.4rem;">
          <tr><th>Metric</th><th style="text-align:right;">Score</th></tr>
          {% for mname, mval in item.metrics.items() %}
          <tr>
            <td>{{ mname }}</td>
            <td style="text-align:right;">{{ "%.4f"|format(mval) }}</td>
          </tr>
          {% endfor %}
        </table>
        {% endif %}
      </div>
      {% endfor %}
    </div>
    {% endif %}

    <!-- Failures -->
    {% if failures %}
    <div class="card">
      <h2>Failures</h2>
      <p class="dim">{{ failures|length }} error(s) encountered.</p>
      <ol style="margin-top:.5rem; padding-left:1.25rem;">
        {% for err in failures %}
        <li><strong>{{ err.type }}</strong>: {{ err.error }}</li>
        {% endfor %}
      </ol>
    </div>
    {% endif %}

    <p class="footer">OpenAgent Eval v{{ version }}</p>
  </div>
</body>
</html>
""",
    autoescape=True,
)


class HTMLReportGenerator(ReportGenerator):
    """Generate a styled HTML report via Jinja2."""

    name = "html"
    description = "Styled HTML report"

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(self, report: EvaluationReport) -> str:
        """Render the report as an HTML string."""
        ctx = self._build_context(report)
        return _HTML_TEMPLATE.render(**ctx)

    def save(self, report: EvaluationReport, output_path: Path) -> Path:
        """Generate and save the HTML report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.generate(report), encoding="utf-8")
        return output_path

    # ------------------------------------------------------------------ #
    # Template context builder                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_context(report: EvaluationReport) -> dict:
        """Build the Jinja2 template context from the evaluation report."""
        summary = report.summary
        total = summary.get("total_items", len(report.result.results))
        errors = summary.get("failed_evaluations", len(report.result.errors))
        success_rate = ((total - errors) / total * 100) if total > 0 else 0.0

        metrics = summary.get("metrics_summary", {})
        if not metrics:
            metrics = report.result.summary.get("metrics", {})

        results = []
        for item in report.result.results:
            results.append(
                {
                    "question": item.question,
                    "answer": item.answer,
                    "ground_truth": item.ground_truth,
                    "metrics": item.metrics,
                }
            )

        failures = [
            {"type": e.get("type", "Unknown"), "error": e.get("error", "No message")}
            for e in report.result.errors
        ]

        return {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total": total,
            "errors": errors,
            "success_rate": success_rate,
            "llm_provider": report.config.llm.provider,
            "model": report.config.llm.model,
            "dataset_path": report.config.dataset.path,
            "metrics": metrics,
            "results": results,
            "failures": failures,
            "version": report.metadata.get("version", "unknown"),
        }
