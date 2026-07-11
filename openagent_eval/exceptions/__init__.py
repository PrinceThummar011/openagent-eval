"""Custom exception hierarchy for OpenAgent Eval.

All exceptions inherit from OpenAgentEvalError for consistent error handling.
"""

from openagent_eval.exceptions.base import OpenAgentEvalError
from openagent_eval.exceptions.cli import CLIError, CommandError, ValidationError
from openagent_eval.exceptions.config import ConfigurationError
from openagent_eval.exceptions.dataset import (
    DatasetError,
    DatasetNotFoundError,
    DatasetValidationError,
    InvalidDatasetError,
)
from openagent_eval.exceptions.metric import (
    MetricError,
    MetricExecutionError,
    MetricNotFoundError,
    MetricTimeoutError,
)
from openagent_eval.exceptions.diagnosis import (
    BlameAttributionError,
    DiagnosisError,
    DiagnosisExecutionError,
)
from openagent_eval.exceptions.plugin import PluginError, PluginLoadError, PluginNotFoundError
from openagent_eval.exceptions.provider import (
    ProviderConnectionError,
    ProviderError,
    ProviderExecutionError,
    ProviderNotFoundError,
)

__all__ = [
    "OpenAgentEvalError",
    "ConfigurationError",
    "DatasetError",
    "DatasetNotFoundError",
    "InvalidDatasetError",
    "DatasetValidationError",
    "MetricError",
    "MetricNotFoundError",
    "MetricExecutionError",
    "MetricTimeoutError",
    "ProviderError",
    "ProviderNotFoundError",
    "ProviderConnectionError",
    "ProviderExecutionError",
    "PluginError",
    "PluginNotFoundError",
    "PluginLoadError",
    "CLIError",
    "CommandError",
    "ValidationError",
    "DiagnosisError",
    "DiagnosisExecutionError",
    "BlameAttributionError",
]
