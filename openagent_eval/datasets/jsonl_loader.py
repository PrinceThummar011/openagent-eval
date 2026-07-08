"""JSONL dataset loader.

Loads datasets from .jsonl files where each line is a separate JSON object.
Supports empty lines and comment lines (starting with #) which are skipped.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openagent_eval.datasets.base import DatasetLoader
from openagent_eval.exceptions.dataset import (
    DatasetNotFoundError,
    DatasetValidationError,
    InvalidDatasetError,
)


class JsonlDatasetLoader(DatasetLoader):
    """Loader for JSONL-formatted datasets.

    Each line in the file should be a valid JSON object.
    Empty lines and lines starting with '#' are skipped.
    """

    name = "jsonl"
    description = "Loads datasets from JSONL files (.jsonl)"

    def load(
        self,
        path: Path,
        limit: int | None = None,
        shuffle: bool = False,
    ) -> list[dict[str, Any]]:
        """Load dataset from a JSONL file.

        Args:
            path: Path to the JSONL file.
            limit: Maximum items to load. None means load all.
            shuffle: Whether to shuffle before limiting.

        Returns:
            List of dataset items as dictionaries.

        Raises:
            DatasetNotFoundError: If the file does not exist.
            InvalidDatasetError: If a line contains invalid JSON.
            DatasetValidationError: If items fail validation.
        """
        if not path.exists():
            raise DatasetNotFoundError(dataset_path=str(path))

        items = self._parse_lines(path)
        self.validate(items)

        if shuffle:
            import random

            random.shuffle(items)

        if limit is not None:
            items = items[:limit]

        return items

    def validate(self, data: list[dict[str, Any]]) -> bool:
        """Validate that all items have at least a 'question' field.

        Args:
            data: List of dataset items to validate.

        Returns:
            True if all items are valid.

        Raises:
            DatasetValidationError: If any item is missing 'question'.
        """
        errors: list[str] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                errors.append(f"Item {i}: expected dict, got {type(item).__name__}")
                continue
            if "question" not in item:
                errors.append(f"Item {i}: missing required field 'question'")
            elif not isinstance(item["question"], str):
                errors.append(f"Item {i}: 'question' must be a string")

        if errors:
            raise DatasetValidationError(
                message=f"Dataset validation failed with {len(errors)} error(s)",
                validation_errors=errors,
            )
        return True

    def _parse_lines(self, path: Path) -> list[dict[str, Any]]:
        """Parse JSONL file line by line.

        Args:
            path: Path to the JSONL file.

        Returns:
            List of parsed item dictionaries.

        Raises:
            InvalidDatasetError: If a line contains invalid JSON.
        """
        items: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                try:
                    item = json.loads(stripped)
                except json.JSONDecodeError as e:
                    raise InvalidDatasetError(
                        message=f"Invalid JSON on line {line_num}: {e}",
                        dataset_path=str(path),
                        format="jsonl",
                        line_number=line_num,
                    ) from e
                items.append(item)
        return items
