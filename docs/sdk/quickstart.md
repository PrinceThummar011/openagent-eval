# Quickstart

!!! note "Prerequisites"
    - Python 3.11+
    - Install the package: `pip install openagent-eval`
    - A compatible LLM provider (e.g., OpenAI) and any required credentials are available as environment variables.

The following example shows the smallest possible workflow: create a configuration, run the evaluation engine on a tiny in‑memory dataset, and print the report summary.

```python
"""Minimal OpenAgent Eval example.
Runs an async engine with a single question and prints the summary.
"""

import asyncio
from pathlib import Path

from openagent_eval.config.models import Config, LLMConfig, RetrieverConfig, MetricsConfig, DatasetConfig
from openagent_eval.core.engine import Engine

# 1️⃣  Build a configuration
config = Config(
    dataset=DatasetConfig(path="data/sample.json", limit=1),
    llm=LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0.0),
    retriever=RetrieverConfig(provider="mock"),  # simple mock retriever
    metrics=MetricsConfig(
        retrieval=[],
        generation=["faithfulness"],
        performance=[],
        cost=[],
    ),
)

# 2️⃣  Create the engine
engine = Engine(config)

# 3️⃣  Define a tiny dataset inline (overrides the path above)
#    The engine expects a list of dicts matching `DatasetItemModel`.
dataset = [
    {
        "question": "What is the capital of France?",
        "ground_truth": "Paris",
        "metadata": {},
    }
]

# 4️⃣  Run the evaluation (async)
async def main():
    report = await engine.run(dataset)
    # The report contains a handy `summary` dict – print the most useful bits.
    print("✅ Evaluation complete")
    print("Total items:", report.summary["total_items"])
    print("Successful:", report.summary["successful_evaluations"])
    print("Metrics summary:", report.summary.get("metrics_summary", {}))
    # Optionally persist the report using ReportManager (see next docs page).

asyncio.run(main())
```

**What you just saw**
- `Config` ties together dataset, LLM, retriever, and metrics.
- `Engine` orchestrates provider construction, pipeline execution, and report generation.
- The example uses the built‑in `mock` retriever so no external service is needed.

Next, dive deeper into the mental model that powers this SDK.

[Next: Concepts →](concepts.md)
