"""Report generation for OpenAgent Eval.

This package provides multiple report formats for evaluation results:

- :class:`TerminalReportGenerator` – Rich-formatted terminal output
- :class:`MarkdownReportGenerator` – Clean Markdown for sharing
- :class:`HTMLReportGenerator` – Styled HTML via Jinja2
- :class:`JSONReportGenerator` – Machine-readable JSON
- :class:`ComparisonReportGenerator` – Side-by-side experiment comparison
- :class:`ReportManager` – Persist and load reports by ID
"""

from __future__ import annotations

from openagent_eval.reports.base import ReportGenerator
from openagent_eval.reports.comparison import ComparisonReportGenerator
from openagent_eval.reports.html import HTMLReportGenerator
from openagent_eval.reports.json_report import JSONReportGenerator
from openagent_eval.reports.manager import ReportManager
from openagent_eval.reports.markdown import MarkdownReportGenerator
from openagent_eval.reports.terminal import (
    TerminalReportGenerator,
    render_to_console,
)

__all__ = [
    "ReportGenerator",
    "TerminalReportGenerator",
    "MarkdownReportGenerator",
    "HTMLReportGenerator",
    "JSONReportGenerator",
    "ComparisonReportGenerator",
    "ReportManager",
    "render_to_console",
]
