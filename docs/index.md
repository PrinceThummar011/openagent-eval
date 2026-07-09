---
hide:
  - navigation
  - toc
---

# OpenAgent Eval

<center>

::: {.center .hero .tx-center}

# OpenAgent Eval
## The `pytest` of AI evaluation

**Open-source, local-first framework for evaluating RAG systems and AI Agents — a clean CLI, a typed Python SDK, and a pluggable metric/provider architecture.**

[Getting Started :octicons-arrow-right-24:](installation.md){ .md-button .md-button--primary }
[View on GitHub :octicons-mark-github-16:](https://github.com/OpenAgentHQ/openagent-eval){ .md-button }

```bash
pip install openagent-eval
```

:::

</center>

---

## Why OpenAgent Eval

<div class="grid cards" markdown>

- :material-rocket-launch: **Local-First**
  Runs entirely on your machine. No dashboards or accounts required — your data never leaves your laptop.

- :material-console-line: **CLI + SDK**
  Drive evaluations from the command line with `oaeval`, or embed `Engine` directly in your Python test suite.

- :material-puzzle: **Framework Agnostic**
  Works with any RAG implementation — LangChain, LlamaIndex, or fully custom pipelines.

- :material-puzzle-plus: **Pluggable**
  Swap LLMs, retrievers, embedders, and metrics through a clean provider/plugin architecture.

- :material-chart-box: **Comprehensive Metrics**
  Retrieval, generation, performance, and cost metrics in one consistent interface.

- :material-file-document-multiple: **Beautiful Reports**
  Terminal, Markdown, HTML, and JSON reports with built-in failure analysis.

</div>

---

## Quick Start

```bash
# Install
pip install openagent-eval

# Create a configuration file
oaeval init

# Run your first evaluation
oaeval run config.yaml

# Inspect the report
oaeval report latest
```

See the [Quickstart](quickstart.md) for a full walkthrough, or jump straight to the
[CLI Reference](cli.md).

---

## Architecture Overview

OpenAgent Eval is a modular, provider-agnostic pipeline. A `Config` describes your dataset, retriever,
LLM, and the metrics to compute. The `Engine` loads the dataset, runs retrieval and generation, scores
the results with the selected metrics, and persists a report.

```mermaid
flowchart LR
    A[Config<br/>config.yaml] --> B[Engine]
    C[Dataset] --> B
    B --> D[Retriever<br/>Provider]
    B --> E[LLM<br/>Provider]
    D --> F[Context]
    E --> G[Answer]
    F --> H[Metrics]
    G --> H
    H --> I[ReportManager<br/>Terminal / MD / HTML / JSON]
```

Every stage is pluggable. Read more on the [Architecture](architecture.md) page.

---

## Evaluation Metrics

Metric names map to the built-in registry (`openagent_eval.metrics.METRIC_REGISTRY`):

<div class="grid cards" markdown>

- :material-magnify: **Retrieval**
  `context_precision`, `context_recall`, `recall_at_k`, `precision_at_k`, `hit_rate`, `mrr`, `ndcg`

- :material-message-text: **Generation**
  `faithfulness`, `answer_relevancy`, `hallucination`, `semantic_similarity`, `exact_match`, `f1_score`, `bleu`, `rouge`, `bertscore`

- :material-timer: **Performance**
  `latency`

- :material-currency-usd: **Cost**
  `token_count`

</div>

---

## Supported Providers

| LLM Providers | Retriever Providers | Embedders |
| --- | --- | --- |
| OpenAI, Google Gemini, Anthropic, Groq, OpenRouter, Ollama, Mock | Chroma, Memory, BM25, FAISS, Qdrant, Pinecone, Weaviate, Elasticsearch, PGVector, HTTP, Mock | Sentence-Transformers, Mock |

Bring your own by implementing the provider base classes — see [API Reference](api.md).

---

## Python SDK

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
print(report.summary)
```

The SDK is fully documented in the [API Reference](api.md) and demonstrated in
[Examples](examples.md).

---

## CLI

| Command | Description |
| --- | --- |
| `oaeval init` | Create a configuration file |
| `oaeval run <config>` | Run an evaluation pipeline |
| `oaeval report <id>` | View a stored report (`latest` for the most recent) |
| `oaeval compare <a> <b>` | Compare two experiments |
| `oaeval list` | List previous evaluations |
| `oaeval doctor` | Check environment and dependencies |

Full command documentation lives in [CLI Reference](cli.md).

---

## Contributing

OpenAgent Eval is community-driven. Contributions of every size are welcome — from bug reports to new
metrics and providers.

- Read the [Contributing Guide](contributing.md)
- Track what's next in the [Roadmap](roadmap.md)
- Find answers in the [FAQ](faq.md)

---

## Community

Stay connected and help shape the roadmap:

- :fontawesome-brands-github: [GitHub](https://github.com/OpenAgentHQ/openagent-eval)
- :fontawesome-brands-x-twitter: [X / Twitter](https://x.com/openagenthq)
- :fontawesome-brands-discord: [Discord](https://discord.gg/openagenthq)
- :octicons-issue-opened-16: [Issues](https://github.com/OpenAgentHQ/openagent-eval/issues)
- :octicons-comment-discussion-16: [Discussions](https://github.com/OpenAgentHQ/openagent-eval/discussions)

---

<div class="center" markdown>

**OpenAgent Eval** &mdash; Apache 2.0 License. Built by the OpenAgent Eval Contributors.

</div>
