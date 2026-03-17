# OpenAI Agents SDK Decision

## Status

Recommended, pending user approval before detailed implementation.

## Decision

Для реализации root-level и subproject-level multi-agent teams в этом workspace рекомендуется использовать:

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- поверх [Responses API / tools layer](https://platform.openai.com/docs/guides/tools)

а не строить весь orchestration runtime как полностью самодельный framework.

## Why this is the best fit

### 1. Это официальный стек именно для агентных систем

Согласно [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), SDK уже даёт необходимые primitives:

- agents;
- tools;
- handoffs;
- guardrails;
- sessions;
- tracing.

Для нашей задачи это важно, потому что мы проектируем не одиночного бота, а систему команд и делегирования.

### 2. SDK поддерживает два ключевых orchestration pattern'а

В [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/) официально описаны:

- `agents as tools` - manager agent держит контроль и вызывает specialist agents как bounded helpers;
- `handoffs` - triage/router agent передаёт управление specialist agent'у.

Это почти идеально совпадает с нашим design target:

- root team нужен manager-style orchestration;
- routing между подпроектами и specialist branches удобно выражать handoff-механикой;
- внутри подпроектов можно комбинировать оба паттерна.

### 3. SDK хорошо сочетается с code-first orchestration

OpenAI docs отдельно подчёркивают ценность code orchestration для более детерминированных workflow.

Это важно для нас, потому что:

- root layer должен быть воспроизводимым;
- часть routing должна быть schema-driven;
- часть решений нужно фиксировать как исследовательские артефакты;
- система должна быть пригодна для статьи, а не только для "магического" промптинга.

### 4. SDK already includes tracing

В [Tracing](https://openai.github.io/openai-agents-python/tracing/) указано, что SDK already records:

- LLM generations;
- tool calls;
- handoffs;
- guardrails;
- custom events.

Для paper-grade traceability это сильное преимущество: мы не начинаем с нуля и можем сразу проектировать runs, logs и evidence around a real trace system.

### 5. SDK совместим с tool/MCP strategy, нужной для Kaggle research

Через [Using tools](https://platform.openai.com/docs/guides/tools) и [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp) платформа уже поддерживает:

- web research;
- function tools;
- remote MCP;
- approval flow;
- logging guidance для tool data sharing.

Это особенно важно для:

- поиска статей;
- извлечения competition context;
- controlled access к external services;
- построения будущих `kaggle-bridge` и `papers-bridge`.

## Recommended application inside this workspace

## Root layer

Root should use Agents SDK as:

- orchestration runtime for root team roles;
- handoff mechanism between root specialists;
- tracing substrate;
- session/context carrier for root-level runs.

Но root не должен превращаться в chat-only system. Root runtime остаётся code-first:

- routing decisions проверяются кодом;
- handoff/result packages materialize в файлах и схемах;
- root logs остаются canonical evidence layer.

## Subproject layer

Каждый подпроект может использовать тот же официальный стек локально, но независимо:

- со своим локальным team topology;
- со своими tool permissions;
- со своей local memory;
- со своими reports и workflows.

Root only coordinates these teams through explicit contracts.

## What we are explicitly not choosing

### Not chosen: fully custom orchestration framework from scratch

Причина:

- выше стоимость поддержки;
- хуже объяснимость для статьи;
- мы теряем official primitives и tracing;
- возрастает риск, что часть логики будет ad-hoc и плохо проверяемой.

### Not chosen: pure prompt-only multi-agent behavior

Причина:

- нам нужна воспроизводимость;
- нужны schema contracts;
- нужны детерминируемые handoff packages;
- нужна test-first разработка runtime layer.

### Not chosen: root-owned local subproject memory

Причина:

- это ломает главный архитектурный инвариант workspace;
- мешает автономии подпроектов;
- делает root слишком тяжёлым и смешивает уровни контекста.

## Recommended implementation style

### Root runtime

Комбинация:

- code-first router;
- structured outputs;
- manager-style root coordinator;
- selective handoffs to root specialists;
- explicit subproject boundary.

### Subproject runtime

Комбинация:

- local lead/manager;
- bounded specialists as tools;
- optional handoffs внутри локальной команды;
- local docs/reports as canonical outputs.

## Minimal technical consequence

Следующая итерация coding должна строиться не вокруг "ещё одной CLI-обёртки", а вокруг adapter layer, который свяжет:

- `workspace_orchestrator/*`
- structured contracts
- root logs
- Agents SDK team runtime

## Open points

1. Какая модель будет базовой для root orchestrator on v1.
2. Какие роли root team будут полноценными agents, а какие останутся code utilities.
3. Какие hosted tools и MCP adapters включать сразу, а какие позже.
4. Нужен ли always-on human approval перед реальным Kaggle submit на первом production cycle.

## Primary sources

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- [Using tools](https://platform.openai.com/docs/guides/tools)
- [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [Tracing](https://openai.github.io/openai-agents-python/tracing/)

## Implementation note (2026-03-17)

This decision is no longer only conceptual.

The workspace now contains a first adapter layer in `workspace_orchestrator/openai_runtime.py` with these properties:

- team specs are derived from the existing organization/ACL substrate;
- shared services are represented as tool-style targets;
- hierarchical calls remain explicit as handoff targets;
- prepared run metadata is propagated into runtime instructions and inspection payloads;
- SDK import is lazy, so the control plane remains testable even when `agents` is absent locally.

Current limitation:

- the environment used for development currently reports `agents` as unavailable, so the implemented layer focuses on inspectable specs and bounded SDK bundle construction rather than live model execution.
