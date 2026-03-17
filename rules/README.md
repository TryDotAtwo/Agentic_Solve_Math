# Root Rules

`rules/` — canonical дерево корневой документации workspace.

Это документация **orchestrator layer**, а не локальная документация подпроектов.

## Read First

Read these documents as the default root context.

### Sequence

1. `../README.md`
2. `../AGENTS.md`
3. `core/PROJECT_MAP.md`
4. `core/RESEARCH_SURVEY.md`
5. `core/DOCUMENTATION_INDEX.md`
6. `logs/USER_PROMPTS_LOG.md`
7. затем локальные документы нужного подпроекта

### Canonical Subfolders

- `core/`
- `workflows/`
- `standards/`
- `registry/`
- `logs/`
- `architecture/`
- `organization/`

### Root Invariant

- корень координирует подпроекты;
- подпроекты остаются самодостаточными и изолированными;
- локальные знания подпроектов не выносятся в корень целиком;
- в root поднимаются только summaries, registry updates, prompts, logs и архитектурные решения.

## Ключевой инвариант

Каждый подпроект рассматривается как самодостаточная и изолированная система со своей локальной документацией, своими правилами и своей собственной мультиагентной командой.

Корень не должен смешивать эти уровни. Root layer only:

- координирует подпроекты;
- хранит global memory and contracts;
- синтезирует межпроектные выводы.

## Canonical structure

Canonical root docs should be read from these subfolders:

- `core/`
- `workflows/`
- `standards/`
- `registry/`
- `logs/`
- `architecture/`
- `organization/`

Only the seven subfolders listed above are canonical.

## What stays in root

This list is now literal. Legacy root compatibility shims were removed during the cleanup on 2026-03-17.

В корне intentionally остаются только bootstrap-файлы, а при невозможности удаления - минимальные compatibility shims:

- `README.md`
- `AGENTS.md`
- `main.py`
- `kaggle_intake/`
- `rules/`
- `workspace_orchestrator/`

## Historical note

Миграция root-level документации в `rules/` начата 2026-03-17.

В старых журналах и historical notes могут встречаться прежние пути из корня. После миграции canonical paths начинаются с `rules/...`.
