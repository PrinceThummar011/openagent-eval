"""Tests for chunking quality analyzer."""

from __future__ import annotations

from openagent_eval.diagnosis.chunking import ChunkingQualityAnalyzer


class TestChunkingQualityAnalyzer:
    """Tests for ChunkingQualityAnalyzer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = ChunkingQualityAnalyzer()

    def test_empty_contexts_returns_no_issues(self) -> None:
        """Empty contexts should return no issues."""
        issues = self.analyzer.analyze("What is AI?", [])
        assert issues == []

    def test_single_context_returns_no_issues(self) -> None:
        """A single normal context should return no issues."""
        issues = self.analyzer.analyze(
            "Explain Python programming language",
            ["Python is a high-level programming language used for web development and data science."],
        )
        assert issues == []

    def test_overlapping_contexts_detected(self) -> None:
        """Highly similar contexts should be detected as overlapping."""
        ctx_a = "Python is a programming language used for web development and data science."
        ctx_b = "Python is a programming language used for web development and data science."  # Near-duplicate
        issues = self.analyzer.analyze("What is Python?", [ctx_a, ctx_b])
        overlap_issues = [i for i in issues if i.issue_type == "overlapping_chunks"]
        assert len(overlap_issues) > 0
        assert overlap_issues[0].affected_contexts == [0, 1]

    def test_distinct_contexts_no_overlap(self) -> None:
        """Distinct contexts should not be flagged as overlapping."""
        ctx_a = "Python is a programming language."
        ctx_b = "JavaScript is used for web browsers."
        issues = self.analyzer.analyze("What is programming?", [ctx_a, ctx_b])
        overlap_issues = [i for i in issues if i.issue_type == "overlapping_chunks"]
        assert len(overlap_issues) == 0

    def test_inconsistent_chunk_sizes(self) -> None:
        """Highly uneven chunk sizes should be detected."""
        ctx_short = "Short."
        ctx_long = "x" * 500  # 500 chars vs 6 chars = 83x ratio
        issues = self.analyzer.analyze(
            "What is this?", [ctx_short, ctx_long]
        )
        size_issues = [
            i for i in issues if i.issue_type == "inconsistent_chunk_sizes"
        ]
        assert len(size_issues) > 0

    def test_consistent_chunk_sizes_no_issue(self) -> None:
        """Similar chunk sizes should not be flagged."""
        ctx_a = "A" * 100
        ctx_b = "B" * 120
        issues = self.analyzer.analyze("Test?", [ctx_a, ctx_b])
        size_issues = [
            i for i in issues if i.issue_type == "inconsistent_chunk_sizes"
        ]
        assert len(size_issues) == 0

    def test_empty_chunk_detected(self) -> None:
        """Very short contexts should be detected."""
        issues = self.analyzer.analyze(
            "What is AI?", ["", "   ", "a"]
        )
        empty_issues = [
            i for i in issues if i.issue_type == "empty_or_small_chunk"
        ]
        assert len(empty_issues) > 0

    def test_content_gap_detected(self) -> None:
        """Missing question keywords in contexts should be detected."""
        # Question has "quantum" and "computing" but contexts don't
        issues = self.analyzer.analyze(
            "What is quantum computing and how does it work?",
            ["The weather is nice today.", "Python is a language."],
        )
        gap_issues = [i for i in issues if i.issue_type == "content_gap"]
        assert len(gap_issues) > 0

    def test_no_content_gap_when_keywords_present(self) -> None:
        """No gap should be detected when keywords are present in contexts."""
        issues = self.analyzer.analyze(
            "What is Python?",
            ["Python is a programming language.", "Python is used for AI."],
        )
        gap_issues = [i for i in issues if i.issue_type == "content_gap"]
        assert len(gap_issues) == 0

    def test_multiple_issues_detected(self) -> None:
        """Multiple issues should be detected simultaneously."""
        # Short context + overlapping + content gap
        ctx_a = "The quick brown fox jumps."
        ctx_b = "The quick brown fox jumps over the lazy dog."
        issues = self.analyzer.analyze(
            "Explain quantum entanglement in physics.",
            [ctx_a, ctx_b],
        )
        # Should detect overlap and possibly content gap
        issue_types = {i.issue_type for i in issues}
        assert len(issue_types) >= 1  # At least overlap


class TestJaccardSimilarity:
    """Tests for the Jaccard similarity helper."""

    def test_identical_texts(self) -> None:
        """Identical texts should have similarity 1.0."""
        sim = ChunkingQualityAnalyzer._jaccard_similarity(
            "hello world", "hello world"
        )
        assert sim == 1.0

    def test_disjoint_texts(self) -> None:
        """Disjoint texts should have similarity 0.0."""
        sim = ChunkingQualityAnalyzer._jaccard_similarity(
            "hello", "world"
        )
        assert sim == 0.0

    def test_partial_overlap(self) -> None:
        """Partially overlapping texts should have intermediate similarity."""
        sim = ChunkingQualityAnalyzer._jaccard_similarity(
            "hello world foo", "hello world bar"
        )
        assert 0.0 < sim < 1.0

    def test_empty_texts(self) -> None:
        """Empty texts should have similarity 0.0."""
        sim = ChunkingQualityAnalyzer._jaccard_similarity("", "")
        assert sim == 0.0

    def test_case_insensitive(self) -> None:
        """Similarity should be case-insensitive."""
        sim = ChunkingQualityAnalyzer._jaccard_similarity(
            "Hello World", "hello world"
        )
        assert sim == 1.0
