# CONTEXT.md - Working Memory

> This file tracks project state, milestones, and current progress.
> Update after every milestone.

---

## Current State

| Field | Value |
|-------|-------|
| **Phase** | Phase 1 Complete |
| **Status** | Foundation Implemented |
| **Last Updated** | 2025-07-08 |
| **Next Action** | Ready for Phase 2 (Data Layer) |

---

## Project Identity

| Field | Value |
|-------|-------|
| **Repository** | openagent-eval |
| **Package** | openagent_eval |
| **CLI** | oaeval |
| **Source of Truth** | PROJECT.md |

---

## Project Understanding

**OpenAgent Eval** is an open-source CLI framework for evaluating RAG systems and AI Agents.

**Core Problem:** Developers can build RAG systems but cannot reliably measure quality, compare experiments, detect hallucinations, or identify retrieval failures.

**Solution:** A local-first, developer-friendly evaluation framework that runs entirely from the command line.

**Target:** Become the `pytest` of AI evaluation.

---

## Architecture Summary

```
CLI (oaeval - Typer + Rich)
            │
            ▼
SDK (openagent_eval - Core Evaluation API)
            │
            ▼
┌─────────────────────────────────────────┐
│  Metrics • Providers • Datasets • Reports │
│  Plugins • Integrations • Exceptions     │
└─────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose |
|------|---------|
| `.ai/00_PROJECT.md` | Single source of truth (Product Specification) |
| `.ai/02_AGENT.md` | Engineering handbook (coding standards, architecture rules) |
| `.ai/03_CONTEXT.md` | This file (working memory, progress tracking) |
| `.ai/04_DECISIONS.md` | Architectural decisions with rationale |
| `.ai/05_TASKS.md` | Project task list and progress tracking |
| `.ai/01_ARCHITECTURE.md` | System architecture and design |

---

## Milestones

### Milestone 0: Documentation & Architecture
- [x] Read and understand PROJECT.md
- [x] Create AGENT.md
- [x] Create CONTEXT.md
- [x] Create DECISIONS.md
- [x] Create TASKS.md
- [x] Architecture analysis and improvements
- [x] Apply architecture decisions (D011-D016)
- [x] Update all project files
- [x] Create .ai/ directory structure

### Milestone 1: Project Foundation
- [x] Initialize project with uv
- [x] Create pyproject.toml
- [x] Set up directory structure
- [x] Create exception hierarchy
- [x] CLI skeleton (Typer)
- [x] Configuration system (Pydantic v2 + YAML)
- [x] Core module (engine, pipeline, executor, registry)
- [x] Testing infrastructure (pytest)
- [x] Linting and formatting (ruff)

### Milestone 2: Data Layer
- [ ] BaseDatasetLoader interface
- [ ] JSON loader
- [ ] JSONL loader
- [ ] CSV loader
- [ ] HuggingFace loader
- [ ] Dataset validation

### Milestone 3: Metrics
- [ ] BaseMetric interface
- [ ] MetricResult model
- [ ] Retrieval metrics
- [ ] Generation metrics
- [ ] Classic metrics (BLEU, ROUGE, etc.)

### Milestone 4: Reports
- [ ] ReportGenerator interface
- [ ] Terminal report (Rich)
- [ ] Markdown report
- [ ] HTML report (Jinja2)
- [ ] JSON report

### Milestone 5: Providers
- [ ] LLMProvider interface
- [ ] Retriever interface
- [ ] OpenAI adapter
- [ ] Gemini adapter
- [ ] Anthropic adapter
- [ ] Chroma adapter

### Milestone 6: Plugin System
- [ ] Plugin registry
- [ ] Entry point discovery
- [ ] User extension examples

---

## Current Questions

None at this time. Phase 1 is complete.

---

## Blockers

None currently.

---

## Architecture Decisions Applied

| ID | Decision | Status |
|----|----------|--------|
| D011 | CLI Naming Convention | ✅ Applied |
| D012 | Core Module Structure | ✅ Applied |
| D013 | Exception Hierarchy | ✅ Applied |
| D014 | Testing Structure | ✅ Applied |
| D015 | Configuration Validation | ✅ Applied |
| D016 | Documentation Workflow | ✅ Applied |

---

## Notes

- Phase 1 is complete - all foundation work done
- 50 tests passing
- CLI functional with all commands (init, run, report, compare, list, doctor)
- Configuration system working with YAML + Pydantic
- Exception hierarchy implemented
- Core module stubs created
- Ready to proceed with Phase 2 (Data Layer)

---

## Change Log

| Date | Change |
|------|--------|
| 2025-07-08 | Initial CONTEXT.md created |
| 2025-07-08 | Updated Milestone 0 completion status |
| 2025-07-08 | Added TASKS.md to key files |
| 2025-07-08 | Architecture analysis completed |
| 2025-07-08 | Applied architecture decisions D011-D016 |
| 2025-07-08 | Updated with project identity (repository, package, CLI) |
| 2025-07-08 | Added ARCHITECTURE.md to key files |
| 2025-07-08 | Created .ai/ directory structure |
| 2025-07-08 | Moved all project files to .ai/ |
| 2025-07-08 | Phase 1 completed - all foundation work done |
| 2025-07-08 | 50 tests passing |
| 2025-07-08 | CLI functional with all commands |
