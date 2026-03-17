# Phase 1 Execution Plan

## Цель

Довести root-level систему до состояния минимально полезного оркестратора без вторжения во внутреннюю жизнь подпроектов.

## Scope

- root launcher;
- workspace discovery;
- intake parser;
- root logs and registry alignment;
- delegation into local `main.py`.

## Concrete Tasks

1. Финализировать `README.md`, `AGENTS.md` и `rules/README.md`.
2. Финализировать канонический индекс `rules/core/DOCUMENTATION_INDEX.md`.
3. Поддержать команды:
   - `overview`
   - `list-subprojects`
   - `parse-intake`
   - `delegate`
4. Зафиксировать root/subproject boundary в архитектурных документах.
5. Подготовить базу для следующей итерации:
   - Kaggle control bridge;
   - papers bridge;
   - handoff package generation.

## Done Criteria

- root-level документы читаются как единая система;
- `main.py` работает как единый launcher;
- root знает, какие подпроекты существуют;
- intake-файл можно разобрать без ручного чтения;
- локальный запуск подпроекта можно делегировать из корня.
