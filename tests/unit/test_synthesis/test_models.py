"""Tests for synthesis data models."""

from __future__ import annotations

import pytest

from openagent_eval.synthesis.models import SyntheticDataset, TestCase, TestCaseType


class TestTestCaseType:
    """Tests for the TestCaseType enum."""

    def test_all_types_exist(self) -> None:
        """Test that all expected types exist."""
        assert TestCaseType.STANDARD.value == "standard"
        assert TestCaseType.UNANSWERABLE.value == "unanswerable"
        assert TestCaseType.AMBIGUOUS.value == "ambiguous"
        assert TestCaseType.MISLEADING.value == "misleading"
        assert TestCaseType.MULTI_HOP.value == "multi_hop"
        assert TestCaseType.COUNTERFACTUAL.value == "counterfactual"

    def test_type_count(self) -> None:
        """Test that we have exactly 6 test types."""
        assert len(TestCaseType) == 6


class TestTestCase:
    """Tests for the TestCase dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic TestCase creation."""
        tc = TestCase(
            question="What is Python?",
            ground_truth="Python is a programming language.",
            context="Python is a high-level language.",
        )
        assert tc.question == "What is Python?"
        assert tc.ground_truth == "Python is a programming language."
        assert tc.context == "Python is a high-level language."
        assert tc.test_type == TestCaseType.STANDARD
        assert tc.source_document == ""
        assert tc.chunk_index == 0
        assert tc.metadata == {}

    def test_creation_with_all_fields(self) -> None:
        """Test TestCase with all fields specified."""
        tc = TestCase(
            question="Why did the project fail?",
            ground_truth="",
            context="The project was completed on time.",
            metadata={"confidence": 0.9},
            test_type=TestCaseType.UNANSWERABLE,
            source_document="report.txt",
            chunk_index=3,
        )
        assert tc.test_type == TestCaseType.UNANSWERABLE
        assert tc.source_document == "report.txt"
        assert tc.chunk_index == 3
        assert tc.metadata == {"confidence": 0.9}

    def test_to_dict(self) -> None:
        """Test TestCase serialization to dict."""
        tc = TestCase(
            question="What is RAG?",
            ground_truth="Retrieval-Augmented Generation.",
            context="RAG combines retrieval and generation.",
            test_type=TestCaseType.STANDARD,
            source_document="docs.txt",
            chunk_index=1,
        )
        d = tc.to_dict()
        assert d["question"] == "What is RAG?"
        assert d["ground_truth"] == "Retrieval-Augmented Generation."
        assert d["context"] == "RAG combines retrieval and generation."
        assert d["test_type"] == "standard"
        assert d["source_document"] == "docs.txt"
        assert d["chunk_index"] == 1
        assert d["metadata"] == {}

    def test_frozen(self) -> None:
        """Test that TestCase is immutable."""
        tc = TestCase(
            question="Test?",
            ground_truth="Answer.",
            context="Context.",
        )
        with pytest.raises(AttributeError):
            tc.question = "Modified"  # type: ignore[misc]


class TestSyntheticDataset:
    """Tests for the SyntheticDataset dataclass."""

    def test_empty_dataset(self) -> None:
        """Test empty dataset creation."""
        ds = SyntheticDataset()
        assert ds.total_count == 0
        assert ds.test_cases == []
        assert ds.type_counts == {}

    def test_dataset_with_cases(self) -> None:
        """Test dataset with test cases."""
        cases = [
            TestCase(
                question="Q1",
                ground_truth="A1",
                context="C1",
                test_type=TestCaseType.STANDARD,
            ),
            TestCase(
                question="Q2",
                ground_truth="A2",
                context="C2",
                test_type=TestCaseType.UNANSWERABLE,
            ),
            TestCase(
                question="Q3",
                ground_truth="A3",
                context="C3",
                test_type=TestCaseType.STANDARD,
            ),
        ]
        ds = SyntheticDataset(test_cases=cases)
        assert ds.total_count == 3
        assert ds.type_counts == {"standard": 2, "unanswerable": 1}

    def test_to_list(self) -> None:
        """Test dataset serialization to list."""
        cases = [
            TestCase(
                question="Q1",
                ground_truth="A1",
                context="C1",
            ),
        ]
        ds = SyntheticDataset(test_cases=cases)
        result = ds.to_list()
        assert len(result) == 1
        assert result[0]["question"] == "Q1"

    def test_to_dict(self) -> None:
        """Test dataset serialization to dict."""
        cases = [
            TestCase(
                question="Q1",
                ground_truth="A1",
                context="C1",
            ),
        ]
        ds = SyntheticDataset(
            test_cases=cases,
            metadata={"source": "test"},
        )
        d = ds.to_dict()
        assert "test_cases" in d
        assert "total_count" in d
        assert "metadata" in d
        assert "type_counts" in d
        assert d["metadata"] == {"source": "test"}
        assert d["total_count"] == 1
