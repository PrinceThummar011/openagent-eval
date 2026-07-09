# Examples

Practical, copy-paste examples for common OpenAgent Eval workflows.

## Minimal CLI evaluation

```bash
oaeval init
oaeval run config.yaml
oaeval report latest
```

## Dataset formats

### JSON

```json title="data/questions.json"
[
  {
    "question": "What is RAG?",
    "ground_truth": "Retrieval-Augmented Generation.",
    "context": "RAG combines retrieval with generation."
  }
]
```

### JSONL

```json title="data/questions.jsonl"
{"question": "What is RAG?", "ground_truth": "Retrieval-Augmented Generation.", "context": "RAG combines retrieval with generation."}
```

### CSV

```csv title="data/questions.csv"
question,ground_truth,context
What is RAG?,Retrieval-Augmented Generation.,"RAG combines retrieval with generation."
```

Format is auto-detected from the file extension (`json`, `jsonl`, `csv`, `pdf`).

## SDK: evaluate in a pytest suite

`Engine.run` is `async`, so wrap it in `asyncio.run`:

```python title="tests/test_eval.py"
import asyncio

from openagent_eval.config.models import Config
from openagent_eval.core.engine import Engine


def test_faithfulness():
    config = Config(
        dataset={"path": "data/questions.json"},
        llm={"provider": "openai", "model": "gpt-4o-mini"},
        retriever={"provider": "chroma", "settings": {"collection_name": "my_collection"}},
        metrics={"generation": ["faithfulness"], "retrieval": ["context_precision"]},
    )
    engine = Engine(config)
    report = asyncio.run(engine.run(dataset))

    assert report.summary["metrics_summary"]["faithfulness"] >= 0.8
    assert report.summary["failed_evaluations"] == 0
```

## SDK: custom metric

Subclass `BaseMetric` and register it in `METRIC_REGISTRY`:

```python title="my_metric.py"
from openagent_eval.metrics.base import BaseMetric, MetricResult
from openagent_eval.metrics import METRIC_REGISTRY


class LengthMetric(BaseMetric):
    name = "length"
    description = "Normalized answer length"

    def evaluate(self, **kwargs) -> MetricResult:
        answer = kwargs.get("answer", "")
        score = min(len(answer.split()) / 100.0, 1.0)
        return MetricResult(score=score, reason=f"{len(answer.split())} words")


METRIC_REGISTRY["length"] = LengthMetric
```

Then reference it in your config: `metrics.generation: [faithfulness, length]`.

See the full template at `openagent_eval/plugins/examples/custom_metric.py`.

## Comparing experiments

```bash
oaeval run config-a.yaml --output json
oaeval run config-b.yaml --output json
oaeval compare exp-001 exp-002
```

## Generating an HTML report

```bash
oaeval run config.yaml --output html
```

Reports are written to `report.output_dir` (default `./reports`).

## Offline dry-run (no API keys)

Use the built-in `mock` providers for CI or local experimentation:

```yaml title="config.yaml"
llm:
  provider: mock
retriever:
  provider: mock
```

## Using a local model (Ollama)

```yaml title="config.yaml"
llm:
  provider: ollama
  model: llama3.1
```

No API key is required.

## Local vector retrieval

Memory/BM25/FAISS retrievers embed locally via an embedder:

```yaml title="config.yaml"
retriever:
  provider: memory
  embedder:
    provider: sentence_transformers
    model: all-MiniLM-L6-v2
```

## Next steps

- Reference the [API Reference](api.md) for every class.
- Run the commands from the [CLI Reference](cli.md).
