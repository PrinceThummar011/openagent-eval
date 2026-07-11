"""Tests for base corpus analyzer."""

from __future__ import annotations

import pytest

from openagent_eval.corpus.base import BaseCorpusAnalyzer
from openagent_eval.corpus.models import AuditReport, CorpusDocument


class DummyAnalyzer(BaseCorpusAnalyzer):
    """Dummy analyzer for testing the base class."""

    name = "dummy"
    description = "A dummy analyzer for testing"

    async def analyze(self, documents, **kwargs):
        return AuditReport(
            corpus_path="",
            total_documents=len(documents),
            checks_performed=[self.name],
        )


class TestBaseCorpusAnalyzer:
    """Tests for BaseCorpusAnalyzer."""

    @pytest.mark.asyncio
    async def test_concrete_analyzer_works(self):
        """Test that a concrete analyzer can be instantiated and run."""
        analyzer = DummyAnalyzer()
        docs = [CorpusDocument(doc_id="a.txt", content="Content")]

        report = await analyzer.analyze(docs)

        assert report.total_documents == 1
        assert "dummy" in report.checks_performed

    @pytest.mark.asyncio
    async def test_validate_inputs_empty(self):
        """Test that empty document list raises error."""
        analyzer = DummyAnalyzer()

        with pytest.raises(ValueError, match="empty"):
            analyzer.validate_inputs([])

    @pytest.mark.asyncio
    async def test_validate_inputs_valid(self):
        """Test that valid documents pass validation."""
        analyzer = DummyAnalyzer()
        docs = [CorpusDocument(doc_id="a.txt", content="Content")]

        # Should not raise
        analyzer.validate_inputs(docs)

    def test_abstract_methods(self):
        """Test that BaseCorpusAnalyzer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseCorpusAnalyzer()  # type: ignore

    def test_name_and_description(self):
        """Test that name and description are set."""
        analyzer = DummyAnalyzer()
        assert analyzer.name == "dummy"
        assert analyzer.description == "A dummy analyzer for testing"
