"""Configuration loader for OpenAgent Eval."""

from __future__ import annotations

from pathlib import Path

import yaml

from openagent_eval.config.models import Config
from openagent_eval.exceptions import ConfigurationError


def load_config(config_path: str | Path) -> Config:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Validated configuration model.

    Raises:
        ConfigurationError: If configuration is invalid or cannot be loaded.
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigurationError(
            message=f"Configuration file not found: {config_path}",
            config_path=str(config_path),
        )

    if not path.suffix in (".yaml", ".yml"):
        raise ConfigurationError(
            message=f"Configuration file must be YAML format (.yaml or .yml): {config_path}",
            config_path=str(config_path),
        )

    try:
        with open(path, encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(
            message=f"Invalid YAML syntax in configuration file: {e}",
            config_path=str(config_path),
        ) from e
    except Exception as e:
        raise ConfigurationError(
            message=f"Failed to read configuration file: {e}",
            config_path=str(config_path),
        ) from e

    if raw_config is None:
        raise ConfigurationError(
            message="Configuration file is empty",
            config_path=str(config_path),
        )

    try:
        # Handle legacy 'dataset' field (string path)
        if isinstance(raw_config.get("dataset"), str):
            raw_config["dataset"] = {"path": raw_config["dataset"]}

        # Handle legacy 'metrics' field (list of strings)
        if isinstance(raw_config.get("metrics"), list):
            metrics_list = raw_config.pop("metrics")
            raw_config["metrics"] = {
                "retrieval": [m for m in metrics_list if m in ("precision", "recall", "mrr", "ndcg", "hit_rate")],
                "generation": [m for m in metrics_list if m in ("faithfulness", "relevancy", "hallucination", "similarity")],
                "performance": [m for m in metrics_list if m in ("latency",)],
                "cost": [m for m in metrics_list if m in ("tokens",)],
            }

        # Handle legacy 'output' field (string format)
        if isinstance(raw_config.get("output"), str):
            output_format = raw_config.pop("output")
            raw_config.setdefault("report", {})["output"] = output_format

        config = Config(**raw_config)
        return config
    except Exception as e:
        raise ConfigurationError(
            message=f"Invalid configuration: {e}",
            config_path=str(config_path),
        ) from e
