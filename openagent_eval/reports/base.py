"""Abstract base class for report generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openagent_eval.core.engine import EvaluationReport


class ReportGenerator(ABC):
    """Abstract base class for all report generators.

    Every report format (Terminal, Markdown, HTML, JSON) implements this
    interface.  Concrete generators must implement both `generate` (produce
    the report as a string) and `save` (write it to disk and return the
    path).
    """

    name: str
    description: str

    @abstractmethod
    def generate(self, report: EvaluationReport) -> str:
        """Generate report content as a string.

        Args:
            report: The complete evaluation report to render.

        Returns:
            The formatted report text.
        """
        ...

    @abstractmethod
    def save(self, report: EvaluationReport, output_path: Path) -> Path:
        """Generate and save the report to a file.

        Args:
            report: The complete evaluation report to render.
            output_path: Destination file path (directories are created
                automatically).

        Returns:
            The path of the saved file.
        """
        ...
