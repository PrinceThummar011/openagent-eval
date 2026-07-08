"""Pydantic models for dataset validation and serialization.

These models enforce the schema for individual dataset items and
the overall dataset structure.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DatasetItem(BaseModel):
    """A single dataset item for evaluation.

    Attributes:
        question: The evaluation question or prompt (required).
        ground_truth: Expected correct answer (optional, needed for some metrics).
        context: Supporting context for the question (optional).
        metadata: Additional metadata for the item (optional).
    """

    question: str = Field(..., description="The evaluation question (required)")
    ground_truth: str | None = Field(None, description="Expected correct answer")
    context: str | None = Field(None, description="Supporting context")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Dataset(BaseModel):
    """A complete dataset containing multiple items.

    Attributes:
        items: List of dataset items.
        metadata: Dataset-level metadata (e.g., source, version).
    """

    items: list[DatasetItem] = Field(default_factory=list, description="Dataset items")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Dataset metadata")
