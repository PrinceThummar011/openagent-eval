"""Dataset loaders for OpenAgent Eval.

This module provides loaders for various dataset formats:
- JSON (.json)
- JSONL (.jsonl)
- CSV (.csv)

Usage:
    >>> from openagent_eval.datasets import load_dataset, JsonDatasetLoader
    >>> from openagent_eval.config.models import DatasetConfig
    >>>
    >>> # Using the factory function
    >>> config = DatasetConfig(path="data/questions.json", limit=100)
    >>> items = load_dataset(config)
    >>>
    >>> # Using a specific loader directly
    >>> loader = JsonDatasetLoader()
    >>> items = loader.load(path=Path("data/questions.json"), limit=100)
"""

from openagent_eval.datasets.base import DatasetLoader
from openagent_eval.datasets.csv_loader import CsvDatasetLoader
from openagent_eval.datasets.factory import load_dataset
from openagent_eval.datasets.json_loader import JsonDatasetLoader
from openagent_eval.datasets.jsonl_loader import JsonlDatasetLoader
from openagent_eval.datasets.models import Dataset, DatasetItem

__all__ = [
    "DatasetLoader",
    "DatasetItem",
    "Dataset",
    "JsonDatasetLoader",
    "JsonlDatasetLoader",
    "CsvDatasetLoader",
    "load_dataset",
]
