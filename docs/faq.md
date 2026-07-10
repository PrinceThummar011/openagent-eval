# FAQ

Frequently asked questions about OpenAgent Eval.

??? question "What is OpenAgent Eval?"
    An open-source, local-first framework for evaluating RAG systems and AI Agents. Our goal is to
    become the `pytest` of AI evaluation — a familiar, composable way to measure quality.

??? question "Do I need an API key?"
    Only if you use a hosted LLM provider (OpenAI, Gemini, Anthropic, Groq, OpenRouter). You can run
    fully locally with [Ollama](https://ollama.com), or use the built-in `mock` providers for CI and
    dry-runs — no API key required.

??? question "Which LLM providers are supported?"
    OpenAI, Google Gemini, Anthropic, Groq, OpenRouter, Ollama, and a `mock` provider. See
    [Architecture](architecture.md#providers-openagent_evalproviders) for the base classes and how to
    add your own.

??? question "Which retrievers are supported?"
    Chroma, Memory, BM25, FAISS, Qdrant, Pinecone, Weaviate, Elasticsearch, PGVector, HTTP, and a
    `mock` provider. Implement `Retriever` to add one.

??? question "Which embedders are supported?"
    Sentence-Transformers and a `mock` embedder. Local vector retrievers (Memory, FAISS, Qdrant,
    Pinecone, PGVector) use an embedder; server-side backends (Chroma, Weaviate) embed remotely.

??? question "Can I use OpenAgent Eval inside pytest?"
    Yes. Construct an `Engine` and call its `async` `run()` method with `asyncio.run`. See
    [Examples](examples.md#sdk-evaluate-in-a-pytest-suite).

??? question "How do I add a custom metric?"
    Subclass `openagent_eval.metrics.base.BaseMetric`, implement `evaluate(**kwargs) -> MetricResult`,
    and register it in `METRIC_REGISTRY`. A template lives at
    `openagent_eval/plugins/examples/custom_metric.py`.

??? question "Which report formats are available?"
    Terminal, Markdown, HTML, and JSON, plus a side-by-side `comparison` report for
    `oaeval compare`.

??? question "Does it send my data anywhere?"
    No. OpenAgent Eval is local-first. The only network calls are to the LLM/retriever providers you
    configure. We do not collect telemetry.

??? question "What Python versions are supported?"
    Python >= 3.11.

??? question "How do I deploy the documentation?"
    Push to `main` — GitHub Actions builds and deploys the site to GitHub Pages automatically. See
    [Contributing](contributing.md#documentation) for local preview.

??? question "Where do I get help?"
    - [GitHub Issues](https://github.com/OpenAgentHQ/openagent-eval/issues) for bugs
    - [GitHub Discussions](https://github.com/OpenAgentHQ/openagent-eval/discussions) for questions
    - [Discord](https://discord.gg/openagenthq) for community chat
