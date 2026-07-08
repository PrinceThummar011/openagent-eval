"""Abstract base class for dataset loaders.

All dataset loaders must implement this interface to ensure consistent
behavior across different file formats (JSON, JSONL, CSV, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DatasetLoader(ABC):
    """Abstract base class for dataset loaders.

    Attributes:
        name: Short identifier for this loader (e.g., "json", "jsonl", "csv").
        description: Human-readable description of what this loader does.
    """

    name: str
    description: str

    @abstractmethod
    def load(
        self,
        path: Path,
        limit: int | None = None,
        shuffle: bool = False,
    ) -> list[dict[str, Any]]:
        """Load dataset from file.

        Args:
            path: Path to the dataset file.
            limit: Maximum number of items to load. None means load all.
            shuffle: Whether to shuffle the dataset before limiting.

        Returns:
            List of dataset items as dictionaries.

        Raises:
            DatasetNotFoundError: If the file does not exist.
            InvalidDatasetError: If the file format is invalid.
            DatasetValidationError: If items fail schema validation.
        """
        ...

    @abstractmethod
    def validate(self, data: list[dict[str, Any]]) -> bool:
        """Validate dataset structure.

        Each item must have at least a "question" field. Optional fields
        include "ground_truth", "context", and "metadata".

        Args:
            data: List of dataset items to validate.

        Returns:
            True if all items are valid.

        Raises:
            DatasetValidationError: If any item fails validation.
        """
        ...
