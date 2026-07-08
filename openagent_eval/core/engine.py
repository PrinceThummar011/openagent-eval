"""Main evaluation engine for OpenAgent Eval."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openagent_eval.config.models import Config
from openagent_eval.core.executor import Executor
from openagent_eval.core.pipeline import Pipeline, PipelineResult
from openagent_eval.core.registry import Registry


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    config: Config
    result: PipelineResult
    summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class Engine:
    """Main evaluation engine that orchestrates the entire evaluation.

    The engine coordinates:
    - Configuration loading
    - Dataset loading
    - Pipeline execution
    - Report generation
    """

    def __init__(self, config: Config) -> None:
        """Initialize the engine.

        Args:
            config: The evaluation configuration.
        """
        self.config = config
        self.registry = Registry()
        self.executor = Executor(
            max_workers=config.max_workers,
            timeout=config.timeout,
        )
        self.pipeline = Pipeline(config)

    async def run(self, dataset: list[dict[str, Any]]) -> EvaluationReport:
        """Run the evaluation engine.

        Args:
            dataset: List of dataset items to evaluate.

        Returns:
            EvaluationReport with results and summary.
        """
        # Execute pipeline
        result = await self.pipeline.execute(dataset)

        # Generate summary
        summary = {
            "total_items": len(dataset),
            "successful_evaluations": len(result.results),
            "failed_evaluations": len(result.errors),
            "metrics_summary": result.summary.get("metrics", {}),
        }

        return EvaluationReport(
            config=self.config,
            result=result,
            summary=summary,
            metadata={
                "version": "0.1.0",
                "engine": "openagent-eval",
            },
        )

    def shutdown(self) -> None:
        """Shutdown the engine and clean up resources."""
        self.executor.shutdown()
