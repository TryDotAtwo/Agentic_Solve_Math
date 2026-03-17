# Documentation Standards

## Purpose

Этот документ задаёт стандарт для root-managed документации.

## Main distinction

Нужно всегда различать:

- root docs;
- local subproject docs.

### Root docs own

- global contracts;
- global routing;
- global memory;
- architecture of the orchestrator;
- cross-project decisions.

### Local docs own

- local workflows;
- local code explanations;
- local experiment logs;
- local hypotheses;
- local results.

## Root doc categories

### Bootstrap

- `README.md`
- `AGENTS.md`
- `main.py`

### Core

- `rules/core/*`

### Workflows

- `rules/workflows/*`

### Standards

- `rules/standards/*`

### Registry

- `rules/registry/*`

### Logs

- `rules/logs/*`

### Architecture

- `rules/architecture/*`

## Required structure for new root docs

```text
# Title

## Purpose
## Scope
## Decisions / content
## Risks / limitations
## Next actions
```

## Status vocabulary

- `planned`
- `in_progress`
- `confirmed`
- `partial`
- `needs_verification`
- `archived`
- `rejected`

## Fact discipline

Если нужно, используйте явные маркеры:

- `Fact`
- `Inference`
- `Hypothesis`
- `Decision`

## Sync rule

После крупных root-level изменений проверять:

- `rules/core/DOCUMENTATION_INDEX.md`
- `rules/core/PROJECT_MAP.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- `rules/logs/RESEARCH_JOURNAL.md`
- необходимость передать update request в локальный подпроект
