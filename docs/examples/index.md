# Examples

Worked examples showing how to use OpenAgent Eval in practice.

## RAG Evaluation Tutorial

A hands-on Jupyter notebook that walks through a complete RAG evaluation:

- Loading a dataset
- Configuring an LLM and retriever
- Running retrieval and generation metrics
- Interpreting the results

**Download:** [`rag_evaluation_tutorial.ipynb`](https://github.com/OpenAgentHQ/openagent-eval/blob/main/examples/rag_evaluation_tutorial.ipynb)

### What you'll learn

| Section | Topic |
|---------|-------|
| 1 | Setting up the environment and config |
| 2 | Loading and inspecting a dataset |
| 3 | Configuring LLM providers (OpenAI, Ollama, Mock) |
| 4 | Configuring retriever providers (Chroma, Memory, BM25) |
| 5 | Running the evaluation pipeline |
| 6 | Understanding retrieval metrics (precision, recall, MRR, NDCG) |
| 7 | Understanding generation metrics (faithfulness, relevancy, hallucination) |
| 8 | Running all 18 metrics together |
| 9 | Interpreting the report output |

### Prerequisites

```bash
pip install openagent-eval jupyter
```

### Quick start

```bash
cd examples/
jupyter notebook rag_evaluation_tutorial.ipynb
```

## More examples

See the [scripts/](https://github.com/OpenAgentHQ/openagent-eval/tree/main/scripts) directory
in the repository for additional runnable examples.
