# CLI Specification

## Overview

OpenAgent Eval provides a CLI interface via `oaeval` built with Typer and Rich. The CLI offers a comprehensive set of commands for evaluating RAG systems, with features like config auto-discovery, shell completion, and machine-readable JSON output.

---

## Installation

```bash
pip install openagent-eval
```

or with uv:

```bash
uv add openagent-eval
```

---

## Global Flags

These flags are available on all commands:

| Flag | Short | Description |
|------|-------|-------------|
| `--quiet` | `-q` | Suppress non-essential output |
| `--json` | | Output machine-readable JSON |
| `--no-color` | | Disable color output |
| `--verbose` | `-v` | Enable verbose output |
| `--version` | `-V` | Show version and exit |
| `--help` | `-h` | Show help message |

---

## Commands

### `oaeval init`

Create a new evaluation configuration.

**Usage:**

```bash
oaeval init [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--config`, `-c` | Path to create configuration file | config.yaml |
| `--force`, `-f` | Overwrite existing configuration file | false |
| `--interactive/--no-interactive` | Use interactive wizard or defaults | --interactive |

**Behavior:**

- Interactively prompts for configuration options (when `--interactive`)
- Creates `config.yaml` in the current directory
- Sets up default metrics and output settings

**Example output:**

```
OpenAgent Eval - Configuration Wizard

Let's set up your evaluation configuration.

1. Dataset Configuration
  Path to dataset file [data/questions.json]:

2. LLM Provider
  1. OpenAI (GPT-4, GPT-4o, etc.)
  2. Anthropic (Claude)
  3. Google Gemini
  4. Groq (fast inference)
  5. OpenRouter (multi-provider)
  Select provider [1]:

3. Model (openai)
  1. GPT-4o (recommended)
  2. GPT-4o Mini (faster, cheaper)
  3. GPT-4 Turbo
  4. GPT-3.5 Turbo (legacy)
  Select model [1]:

4. Retriever
  1. ChromaDB (local, default)
  2. Qdrant
  3. Pinecone (cloud)
  4. Weaviate
  5. FAISS (local)
  6. In-memory (testing)
  Select retriever [1]:

5. Metrics
  1. Quick (3 metrics) - Fast, basic evaluation
  2. Standard (5 metrics) - Balanced (recommended)
  3. Comprehensive (9 metrics) - Thorough, slower
  Select metric preset [2]:

6. Output Format
  1. terminal - Rich terminal output
  2. markdown - Markdown file
  3. html - HTML report
  4. json - JSON data
  Select output format [1]:

Configuration generated successfully!

OK Configuration created: config.yaml

Next steps:
  1. Review the configuration file
  2. Run 'oaeval validate' to check it
  3. Run 'oaeval run' to start evaluation
```

---

### `oaeval validate`

Validate configuration without running evaluation.

**Usage:**

```bash
oaeval validate [CONFIG_PATH]
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `CONFIG_PATH` | Path to configuration file | No (auto-discovered) |

**Behavior:**

- Validates YAML syntax
- Checks configuration schema
- Verifies API key availability
- Validates dataset file existence
- Shows warnings and recommendations

**Example output:**

```
OpenAgent Eval - Configuration Validator
Config: config.yaml

1. Checking YAML syntax...
  OK YAML syntax valid

2. Validating configuration schema...
  OK Configuration schema valid

3. Checking API keys...
  OK All required API keys configured

4. Checking dataset...
  OK Dataset found: data/questions.json
  Size: 12.5 KB

5. Checking output directory...
  OK Output directory exists: ./reports

6. Checking provider configuration...
  LLM: openai (gpt-4o)
  Retriever: chroma

7. Checking metrics...
  Configured: 5 metrics
    Retrieval: context_precision, context_recall, mrr
    Generation: faithfulness, answer_relevancy
    Performance: latency
    Cost: token_count

Summary:
PASSED Configuration is valid

Ready to run: oaeval run <config>
```

---

### `oaeval run`

Run an evaluation.

**Usage:**

```bash
oaeval run [CONFIG_PATH] [OPTIONS]
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `CONFIG_PATH` | Path to configuration file | No (auto-discovered) |

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Override output format (terminal, markdown, html, json) | None |
| `--verbose` | `-v` | Enable verbose output | false |
| `--dry-run` | | Validate config and show evaluation plan without running | false |
| `--metrics` | `-m` | Comma-separated list of metrics to run (overrides config) | None |

**Example:**

```bash
oaeval run config.yaml --output markdown --output-dir ./reports
oaeval run config.yaml --dry-run
oaeval run config.yaml --metrics faithfulness,answer_relevancy,latency
```

**Example output (normal run):**

```
OpenAgent Eval v0.1.0
Configuration: config.yaml

Loaded 500 items
Running evaluation (500 items)...
████████████████████████████████ 100% 0:02:05
Complete!

OK Evaluation complete!
Items: 500 | Errors: 0
Report saved to: reports/eval_2024_01_15.json
```

**Example output (dry run):**

```
OpenAgent Eval - Dry Run Mode

Configuration Summary:
  Config file: config.yaml
  Dataset: data/questions.json
  LLM: openai (gpt-4o)
  Retriever: chroma
  Output: terminal
  Output dir: ./reports

Metrics (5):
  Retrieval: context_precision, context_recall, mrr
  Generation: faithfulness, answer_relevancy
  Performance: latency
  Cost: token_count

Dataset:
  OK Loaded 500 items

  Sample item:
    question: What is the capital of France?
    answer: Paris is the capital of France.
    ground_truth: Paris

This was a dry run. No evaluations were performed.
Run 'oaeval run <config>' to execute the evaluation.
```

---

### `oaeval report`

View evaluation reports.

**Usage:**

```bash
oaeval report <REPORT_ID|latest> [OPTIONS]
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `REPORT_ID` | Report ID or 'latest' for the most recent report | Yes |

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output format (terminal, markdown, html, json) | terminal |
| `--output-dir` | `-d` | Directory where reports are stored | ./reports |

**Example:**

```bash
oaeval report latest
oaeval report exp_2024_01_15 --output markdown
oaeval report latest --json
```

---

### `oaeval compare`

Compare two or more experiments.

**Usage:**

```bash
oaeval compare <EXPERIMENT_A> <EXPERIMENT_B> [OPTIONS]
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `EXPERIMENT_A` | First experiment ID or path | Yes |
| `EXPERIMENT_B` | Second experiment ID or path | Yes |

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--metrics` | `-m` | Specific metrics to compare (default: all) | None |
| `--output-dir` | `-d` | Directory where reports are stored | ./reports |

**Example:**

```bash
oaeval compare exp_a exp_b
oaeval compare exp_a exp_b --metrics faithfulness,answer_relevancy
```

**Example output:**

```
Experiment Comparison

| Metric           | Experiment A | Experiment B | Delta |
|------------------|--------------|--------------|-------|
| Faithfulness     | 83.2%        | 92.1%        | +8.9% |
| Answer Relevancy | 81.5%        | 89.7%        | +8.2% |
| Latency          | 450ms        | 612ms        | +162ms|
| Cost             | $1.82        | $2.17        | +$0.35|

Winner: Experiment B (Faithfulness +8.9%)
```

---

### `oaeval list`

List previous evaluations.

**Usage:**

```bash
oaeval list [OPTIONS]
```

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--limit` | `-l` | Number of evaluations to show | 10 |
| `--output` | `-o` | Filter by output format | None |
| `--output-dir` | `-d` | Directory where reports are stored | ./reports |
| `--sort` | `-s` | Sort by (date, score, cost) | date |
| `--reverse` | `-r` | Reverse sort order | false |
| `--search` | | Search reports by config path or ID | None |

**Example:**

```bash
oaeval list --limit 5 --sort score
oaeval list --search "data/questions" --sort date
oaeval list --output json --limit 10
```

**Example output:**

```
Recent Evaluations

| ID                  | Date       | Config            | Status |
|---------------------|------------|-------------------|--------|
| exp_2024_01_15_001  | 2024-01-15 | data/questions.json | OK     |
| exp_2024_01_14_003  | 2024-01-14 | data/questions.json | OK     |
| exp_2024_01_13_002  | 2024-01-13 | data/custom.json  | FAILED |

Showing 3 evaluations
```

---

### `oaeval delete`

Delete evaluation reports.

**Usage:**

```bash
oaeval delete <REPORT_ID|all> [OPTIONS]
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `REPORT_ID` | Report ID to delete, or 'all' to delete all reports | Yes |

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output-dir` | `-d` | Directory where reports are stored | ./reports |
| `--force` | `-f` | Skip confirmation prompt | false |

**Example:**

```bash
oaeval delete exp_2024_01_15_001
oaeval delete all --force
```

**Example output:**

```
Delete Reports

Report to delete: exp_2024_01_15_001
Created: 2024-01-15T10:30:00Z

Are you sure you want to delete this report? [y/N]: y

OK Deleted report: exp_2024_01_15_001
```

---

### `oaeval doctor`

Check environment and dependencies.

**Usage:**

```bash
oaeval doctor [OPTIONS]
```

**Options:**

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Show detailed information | false |
| `--check-api` | | Test API connectivity (requires API keys) | false |

**Example output:**

```
OpenAgent Eval - Environment Check

Environment Status
  Component       Status    Details
  Python          OK        v3.11.5
  openagent-eval  OK        v0.1.0
  typer           OK        CLI framework
  rich            OK        Terminal UI
  pydantic        OK        Data validation

API Key Availability
  Provider      Environment Variable    Status
  OpenAI        OPENAI_API_KEY          Available
  Gemini        GEMINI_API_KEY          Not set
  Anthropic     ANTHROPIC_API_KEY       Available
  Groq          GROQ_API_KEY            Not set

Configuration:
  OK Found config: config.yaml

Summary:
  OK Python version is compatible
  OK Available providers: OpenAI, Anthropic

Recommendations
  - Set GEMINI_API_KEY for Gemini support
  - Set GROQ_API_KEY for Groq support
```

---

### `oaeval completion`

Generate shell completion script.

**Usage:**

```bash
oaeval completion <SHELL>
```

**Arguments:**

| Argument | Description | Required |
|----------|-------------|----------|
| `SHELL` | Shell to generate completion for (bash, zsh, fish) | Yes |

**Example:**

```bash
# Install completion
oaeval completion bash >> ~/.bashrc
oaeval completion zsh >> ~/.zshrc
oaeval completion fish > ~/.config/fish/completions/oaeval.fish

# Or just view the script
oaeval completion bash
```

---

## Configuration File

### Example `config.yaml`

```yaml
dataset: data/questions.json

retriever:
  provider: chroma
  settings:
    collection_name: my_docs
    persist_directory: ./chroma_db

llm:
  provider: openai
  model: gpt-4o
  temperature: 0.0

metrics:
  retrieval:
    - context_precision
    - context_recall
    - mrr
  generation:
    - faithfulness
    - answer_relevancy
  performance:
    - latency
  cost:
    - token_count

report:
  output: terminal
  output_dir: ./reports
```

### Configuration Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset.path` | string | Yes | - | Path to dataset file |
| `retriever.provider` | string | Yes | - | Retriever provider name |
| `retriever.settings` | object | No | {} | Provider-specific settings |
| `llm.provider` | string | Yes | - | LLM provider name |
| `llm.model` | string | Yes | - | Model identifier |
| `llm.temperature` | float | No | 0.0 | Sampling temperature |
| `metrics.retrieval` | list | No | all | Retrieval metrics |
| `metrics.generation` | list | No | all | Generation metrics |
| `metrics.performance` | list | No | all | Performance metrics |
| `metrics.cost` | list | No | all | Cost metrics |
| `report.output` | string | No | terminal | Report format |
| `report.output_dir` | string | No | ./reports | Output directory |

---

## Config Auto-Discovery

OpenAgent Eval automatically finds your configuration file in the following order:

1. **Explicit path**: Command argument (e.g., `oaeval run config.yaml`)
2. **Environment variable**: `OAEVAL_CONFIG`
3. **Current directory**: `config.yaml`, `config.yml`, `oaeval.yaml`, `oaeval.yml`
4. **Parent directories**: Walks up to filesystem root

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI |
| `GEMINI_API_KEY` | Google Gemini API key | For Gemini |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Anthropic |
| `GROQ_API_KEY` | Groq API key | For Groq |
| `OPENROUTER_API_KEY` | OpenRouter API key | For OpenRouter |
| `OAEVAL_CONFIG` | Path to configuration file | No |

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Dataset error |
| 4 | Provider error |
| 5 | Metric error |
