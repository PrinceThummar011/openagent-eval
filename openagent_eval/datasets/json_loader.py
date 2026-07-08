"""JSON dataset loader.

Loads datasets from .json files. Supports two formats:
1. A JSON array of objects: [{"question": "..."}, ...]
2. A JSON object with an "items" key: {"items": [{"question": "..."}, ...]}

Each item must have at least a "question" field.
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


class JsonDatasetLoader(DatasetLoader):
    """Loader for JSON-formatted datasets.

    Supports both array format and object-with-items format.
    """

    name = "json"
    description = "Loads datasets from JSON files (.json)"

    def load(
        self,
        path: Path,
        limit: int | None = None,
        shuffle: bool = False,
    ) -> list[dict[str, Any]]:
        """Load dataset from a JSON file.

        Args:
            path: Path to the JSON file.
            limit: Maximum items to load. None means load all.
            shuffle: Whether to shuffle before limiting.

        Returns:
            List of dataset items as dictionaries.

        Raises:
            DatasetNotFoundError: If the file does not exist.
            InvalidDatasetError: If the JSON is malformed or has unexpected structure.
            DatasetValidationError: If items fail validation.
        """
        if not path.exists():
            raise DatasetNotFoundError(dataset_path=str(path))

        try:
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise InvalidDatasetError(
                message=f"Invalid JSON in file: {e}",
                dataset_path=str(path),
                format="json",
            ) from e

        items = self._extract_items(raw_data, path)
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

    def _extract_items(
        self, raw_data: Any, path: Path
    ) -> list[dict[str, Any]]:
        """Extract items list from parsed JSON data.

        Args:
            raw_data: Parsed JSON data (list or dict).
            path: File path for error reporting.

        Returns:
            List of item dictionaries.

        Raises:
            InvalidDatasetError: If structure is not recognized.
        """
        if isinstance(raw_data, list):
            return raw_data

        if isinstance(raw_data, dict):
            if "items" in raw_data:
                items = raw_data["items"]
                if isinstance(items, list):
                    return items
                raise InvalidDatasetError(
                    message="Field 'items' must be a list",
                    dataset_path=str(path),
                    format="json",
                )
            raise InvalidDatasetError(
                message="JSON object must contain an 'items' key or be a list",
                dataset_path=str(path),
                format="json",
            )

        raise InvalidDatasetError(
            message=f"Expected list or dict, got {type(raw_data).__name__}",
            dataset_path=str(path),
            format="json",
        )
