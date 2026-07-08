"""CSV dataset loader.

Loads datasets from .csv files using Python's built-in csv module.
Column headers are mapped to item field names.
Required column: "question"
Optional columns: "ground_truth", "context", "metadata"
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from openagent_eval.datasets.base import DatasetLoader
from openagent_eval.exceptions.dataset import (
    DatasetNotFoundError,
    DatasetValidationError,
    InvalidDatasetError,
)

# Fields that are recognized as dataset item fields
KNOWN_FIELDS = {"question", "ground_truth", "context", "metadata"}


class CsvDatasetLoader(DatasetLoader):
    """Loader for CSV-formatted datasets.

    The CSV must have a header row. The 'question' column is required.
    All other columns are optional and mapped to their respective fields.
    """

    name = "csv"
    description = "Loads datasets from CSV files (.csv)"

    def load(
        self,
        path: Path,
        limit: int | None = None,
        shuffle: bool = False,
    ) -> list[dict[str, Any]]:
        """Load dataset from a CSV file.

        Args:
            path: Path to the CSV file.
            limit: Maximum items to load. None means load all.
            shuffle: Whether to shuffle before limiting.

        Returns:
            List of dataset items as dictionaries.

        Raises:
            DatasetNotFoundError: If the file does not exist.
            InvalidDatasetError: If the CSV is malformed or missing required columns.
            DatasetValidationError: If items fail validation.
        """
        if not path.exists():
            raise DatasetNotFoundError(dataset_path=str(path))

        items = self._parse_csv(path)
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

    def _parse_csv(self, path: Path) -> list[dict[str, Any]]:
        """Parse CSV file into list of item dictionaries.

        Args:
            path: Path to the CSV file.

        Returns:
            List of parsed item dictionaries.

        Raises:
            InvalidDatasetError: If CSV is malformed or missing 'question' column.
        """
        try:
            with path.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    raise InvalidDatasetError(
                        message="CSV file is empty or has no header row",
                        dataset_path=str(path),
                        format="csv",
                    )

                if "question" not in reader.fieldnames:
                    raise InvalidDatasetError(
                        message=f"CSV missing required 'question' column. Found: {list(reader.fieldnames)}",
                        dataset_path=str(path),
                        format="csv",
                    )

                items: list[dict[str, Any]] = []
                for row_num, row in enumerate(reader, start=2):
                    item = self._map_row(row)
                    items.append(item)
                return items
        except csv.Error as e:
            raise InvalidDatasetError(
                message=f"CSV parsing error: {e}",
                dataset_path=str(path),
                format="csv",
            ) from e

    def _map_row(self, row: dict[str, str | None]) -> dict[str, Any]:
        """Map a CSV row dict to a dataset item dict.

        Empty strings are converted to None for optional fields.
        The 'metadata' field, if present, is kept as a string (caller
        can parse JSON if needed).

        Args:
            row: Row from csv.DictReader.

        Returns:
            Mapped dataset item dictionary.
        """
        item: dict[str, Any] = {}

        # Always include question (will be validated later)
        question = row.get("question", "")
        item["question"] = question if question else ""

        # Optional fields
        for field in ("ground_truth", "context"):
            value = row.get(field)
            item[field] = value if value else None

        # Metadata as raw string (CSV doesn't natively support nested objects)
        metadata_str = row.get("metadata")
        if metadata_str:
            item["metadata"] = {"raw": metadata_str}
        else:
            item["metadata"] = {}

        return item
