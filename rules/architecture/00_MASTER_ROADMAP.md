# Master Roadmap

## Purpose

Этот документ фиксирует первый крупный этап перестройки workspace в научно ориентированную мультиагентную систему.

## Stage 1 Goal

Создать root-level мультиагентную систему, которая способна:

- принимать Kaggle задачи через intake;
- выделять или создавать изолированные подпроекты;
- читать official files и descriptions;
- собирать источники и статьи;
- организовывать локальные мультиагентные команды;
- готовить и отправлять submission;
- сохранять научную трассируемость.

## Non-goals of the current session

- полная реализация self-improvement loop;
- full production code for every agent role;
- унификация всех старых подпроектов за один проход.

## Phases

### Phase 0. Root restructuring

- ввести canonical `rules/` tree;
- очистить роль корня;
- зафиксировать архитектурные инварианты.

### Phase 1. Root orchestrator design

- спроектировать root launcher;
- описать системные слои;
- определить протоколы обмена между агентами.

### Phase 2. Kaggle-first execution stack

- intake parsing;
- official contract capture;
- source collection;
- local team activation;
- submission workflow.

### Phase 3. Local autonomous project teams

- engineering team;
- math/theory team;
- literature team;
- synthesis/reporting team.

### Phase 4. Shared services

- MCP layer;
- artifact registry;
- prompt and evidence storage;
- submission and leaderboard tracking.

### Phase 5. Reproducibility and paper-readiness

- evidence model;
- decision records;
- experiment provenance;
- canonical summaries.

## Immediate deliverables of this session

- new root documentation layout;
- explicit invariants;
- detailed architecture docs;
- MCP strategy;
- migration notes and risk register.
