# Implementation Roadmap

## Phase 0 - Root Cleanup

### Goal

Сделать корень понятным control plane.

### Deliverables

- `rules/` hierarchy
- новый `README.md`
- новый `AGENTS.md`
- обновлённый root launcher

### Done Criteria

- root docs убраны из плоского корня;
- читающий агент сразу видит границу root vs subproject.

## Phase 1 - Root Orchestration Scaffold

### Goal

Дать root-level системе минимальный рабочий runtime.

### Deliverables

- workspace discovery
- intake parser
- subproject registry snapshot
- subproject delegation command

### Done Criteria

- `python main.py overview`
- `python main.py list-subprojects`
- `python main.py parse-intake <file>`
- `python main.py delegate <subproject>`

## Phase 2 - Research Automation

### Goal

Научить root-level агент собирать глубокий research package.

### Deliverables

- source classification
- initial brief generation
- baseline idea extraction
- paper/repo/notebook discovery plan
- structured handoff package

## Phase 3 - Kaggle Ops Layer

### Goal

Сделать безопасный production-grade путь до сабмита.

### Deliverables

- Kaggle control layer
- submission validators
- submission logs
- retry and failure taxonomy

## Phase 4 - Multi-Project Coordination

### Goal

Связать сразу несколько изолированных подпроектов через root synthesis.

### Deliverables

- cross-project summaries
- dependency tracking
- architecture decision logs
- shared article themes

## Phase 5 - Paper-Grade Traceability

### Goal

Подготовить систему к написанию статьи.

### Deliverables

- decision lineage
- source lineage
- artifact lineage
- stable status vocabulary
- export-friendly summaries

## Current Priority

Сейчас в фокусе `Phase 0` и `Phase 1`, чтобы следующая итерация кодинга уже шла по чёткой архитектурной спецификации.
