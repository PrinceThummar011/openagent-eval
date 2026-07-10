# API Reference

OpenAgent Eval exposes a small, stable public API for embedding evaluations in Python code and tests.
All examples use the real, current interfaces (the engine is `async`).

## Configuration

### `Config` and sub-models

```python
from openagent_eval.config.models import (
    Config, LLMConfig, RetrieverConfig, EmbedderConfig,
    MetricsConfig, DatasetConfig, ReportConfig,
)

config = Config(
    dataset=DatasetConfig(path="data/questions.json", limit=100),
    llm=LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0.0),
    retriever=RetrieverConfig(
        provider="chroma",
        settings={"collection_name": "my_collection"},
    ),
    metrics=MetricsConfig(
        retrieval=["context_precision", "context_recall", "mrr"],
        generation=["faithfulness", "answer_relevancy"],
        performance=["latency"],
        cost=["token_count"],
    ),
)
```

### `load_config`

Load and validate a YAML file (also normalizes legacy config shapes):

```python
from openagent_eval.config.loader import load_config

config = load_config("config.yaml")
```

## Engine

### `Engine`

The top-level orchestrator. Construct it with a `Config` (or inject providers/metrics directly), then
call the `async` `run()` method with a list of dataset items.

```python
import asyncio

from openagent_eval.config.models import Config
from openagent_eval.core.engine import Engine

config = Config(
    dataset={"path": "data/questions.json"},
    llm={"provider": "openai", "model": "gpt-4o-mini"},
    retriever={"provider": "chroma", "settings": {"collection_name": "my_collection"}},
)

engine = Engine(config)
report = asyncio.run(engine.run(dataset))
```

| Parameter | Type | Description |
| --- | --- | --- |
| `config` | `Config` | The evaluation configuration |
| `retriever` | `Retriever` \| `None` | Injected retriever (overrides config) |
| `llm` | `LLMProvider` \| `None` | Injected LLM provider (overrides config) |
| `metrics` | `list[tuple[str, BaseMetric]]` \| `None` | Injected metrics (overrides config) |

`await engine.run(dataset)` returns an `EvaluationReport`.

### `EvaluationReport`

| Attribute | Type | Description |
| --- | --- | --- |
| `config` | `Config` | The configuration used |
| `result` | `PipelineResult` | Per-item results and errors |
| `summary` | `dict` | Aggregate summary (`total_items`, `successful_evaluations`, `failed_evaluations`, `metrics_summary`, `total_tokens`, `average_latency_ms`) |
| `metadata` | `dict` | Engine version and provider names |

```python
print(report.summary["metrics_summary"])
print(report.summary["average_latency_ms"])
```

## Datasets

`openagent_eval.datasets` loads files into validated items.

```python
from openagent_eval.config.models import DatasetConfig
from openagent_eval.datasets.factory import load_dataset

items = load_dataset(DatasetConfig(path="data/questions.json", limit=100))
```

Supported formats: `json`, `jsonl`, `csv`, `pdf` (auto-detected from extension, or set `format`).

`DatasetItemModel` fields: `question` (required), `ground_truth`, `context`,
`ground_truth_contexts`, `metadata`, `contexts`.

## Providers

### `LLMProvider` (base)

```python
from openagent_eval.providers.base import LLMProvider

class MyLLM(LLMProvider):
    name = "my_llm"
    description = "A custom LLM provider"

    async def generate(self, prompt: str, **kwargs) -> str:
        ...

    async def get_token_count(self, text: str) -> int:
        ...
```

Built-in implementations live under `openagent_eval.providers.llm` (openai, gemini, anthropic, groq,
openrouter, ollama, mock).

### `Retriever` (base)

```python
from openagent_eval.providers.base import Retriever
from openagent_eval.providers.models import Document

class MyRetriever(Retriever):
    name = "my_retriever"
    description = "A custom retriever"

    async def retrieve(self, query: str, k: int = 5) -> list[Document]:
        ...
```

Built-in implementations live under `openagent_eval.providers.retrievers` (chroma, memory, bm25, faiss,
qdrant, pinecone, weaviate, elasticsearch, pgvector, http, mock).

### `Embedder` (base)

`openagent_eval.providers.embedders.base.Embedder` is the interface for local embedding backends
(Sentence-Transformers, Mock). Used by vector retrievers that embed locally.

## Metrics

All metrics implement `openagent_eval.metrics.base.BaseMetric`:

```python
from openagent_eval.metrics.base import BaseMetric, MetricResult

class MyMetric(BaseMetric):
    name = "my_metric"
    description = "A custom metric"

    def evaluate(self, **kwargs) -> MetricResult:
        return MetricResult(score=1.0, reason="Always correct", metadata={})
```

`MetricResult` is a frozen dataclass with `score` (0.0–1.0), `reason`, and `metadata`.

### Registry

```python
from openagent_eval.metrics import METRIC_REGISTRY, get_metric, list_metrics

get_metric("faithfulness")        # -> Faithfulness class
list_metrics()                     # -> sorted list of metric names
```

Register a custom metric by adding it to the registry:

```python
from openagent_eval.metrics import METRIC_REGISTRY
from my_metric import MyMetric

METRIC_REGISTRY["my_metric"] = MyMetric
```

Available metric names: `context_precision`, `context_recall`, `recall_at_k`, `precision_at_k`,
`hit_rate`, `mrr`, `ndcg`, `faithfulness`, `answer_relevancy`, `hallucination`, `semantic_similarity`,
`exact_match`, `f1_score`, `bleu`, `rouge`, `bertscore`, `latency`, `token_count`.

## Reports

`openagent_eval.reports.manager.ReportManager` persists and loads reports:

```python
from openagent_eval.reports.manager import ReportManager
from pathlib import Path

manager = ReportManager()
path = manager.save_report(report, output_dir=Path("./reports"))
data = manager.get_latest_report(Path("./reports"))
report = manager.reconstruct(data)
```

| Method | Description |
| --- | --- |
| `save_report(report, output_dir, report_id=None)` | Persist a report as JSON |
| `load_report(report_id, output_dir)` | Load a report by ID |
| `list_reports(output_dir)` | List reports (newest first) |
| `get_latest_report(output_dir)` | Load the most recent report |
| `reconstruct(data)` | Rebuild an `EvaluationReport` from a dict |

Report formats: `terminal`, `markdown`, `html`, `json`, `comparison`.

## Plugins

`openagent_eval.plugins.PluginManager` manages the plugin lifecycle (discovery, loading, querying).
It is initialized with the central `Registry`:

```python
from openagent_eval.core.registry import Registry
from openagent_eval.plugins import PluginManager

manager = PluginManager(Registry())
manager.initialize()                      # load all discovered plugins
manager.get_available_plugins()          # group -> [names]
```

Custom metrics/providers are typically shipped as packages that register themselves via entry points;
you can also add them directly to `METRIC_REGISTRY` (see above). See
`openagent_eval/plugins/examples/custom_metric.py` for a template.

## Exceptions

All errors derive from `openagent_eval.exceptions.OpenAgentEvalError`:

```python
from openagent_eval.exceptions import (
    ConfigurationError, DatasetError, MetricError,
    ProviderError, PluginError, CLIError,
)
```

## Next steps

- Put it together in [Examples](examples.md).
- Understand the moving parts in [Architecture](architecture.md).
