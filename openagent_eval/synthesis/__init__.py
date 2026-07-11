"""Synthetic test data generation module for OpenAgent Eval.

Provides tools to auto-generate Q&A test cases and adversarial scenarios
from a knowledge base, solving the "not enough test cases" problem.

Usage::

    from openagent_eval.synthesis import SyntheticDataGenerator

    generator = SyntheticDataGenerator(llm_provider=openai_provider)
    dataset = await generator.generate(
        corpus_path="./knowledge_base/",
        count=100,
        adversarial=True,
    )

    print(dataset.total_count)      # Total test cases
    print(dataset.type_counts)      # Breakdown by type
"""

from openagent_eval.synthesis.adversarial import AdversarialTestCaseGenerator
from openagent_eval.synthesis.generator import SyntheticDataGenerator
from openagent_eval.synthesis.models import (
    SyntheticDataset,
    TestCase,
    TestCaseType,
)
from openagent_eval.synthesis.question_gen import QuestionGenerator

__all__ = [
    "AdversarialTestCaseGenerator",
    "QuestionGenerator",
    "SyntheticDataGenerator",
    "SyntheticDataset",
    "TestCase",
    "TestCaseType",
]
