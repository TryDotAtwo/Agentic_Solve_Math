# Research and Design Program

## Final target

Наша целевая система должна работать так:

1. Пользователь запускает `main.py` в корне workspace.
2. Корневой runtime поднимает **root multi-agent team** как global research/orchestration layer.
3. Root team:
   - принимает новую задачу или intake;
   - определяет тип работы;
   - обновляет глобальную память и трассировку;
   - выбирает существующий подпроект или создаёт новый;
   - активирует **локальную multi-agent team подпроекта**;
   - получает назад только summary, статусы, артефакты и escalation-запросы.
4. Внутри каждого подпроекта живёт своя автономная исследовательская команда со своей локальной документацией, правилами и runtime.
5. Root не хранит локальную рабочую память подпроектов у себя и не подменяет их domain-specific логику.

Это и есть целевое состояние "meta-orchestrator above autonomous subproject teams".

## Current phase

Текущий этап не про полный coding всей системы, а про **исследование + фиксацию проектных решений** перед кодингом.

Выходом текущего этапа должны стать:

- чёткий исследовательский план;
- выбранный официальный framework;
- рекомендуемая topology root/team и subproject/team;
- рекомендуемая hierarchical department model;
- зафиксированные handoff/result protocols;
- зафиксированная access-control model;
- рекомендация по tool/MCP stack;
- подробный TDD-план следующей фазы реализации;
- явный список решений, которые надо согласовать с пользователем до активной разработки.

## Initial research questions

Перед исследованием были зафиксированы такие ключевые вопросы:

1. Какой официальный OpenAI framework лучше всего подходит для построения multi-agent teams?
2. Какая архитектура позволит сохранить строгую границу между root layer и автономными подпроектами?
3. Какие инженерные паттерны стоит перенять из `CayleyPy_Pancake/`?
4. Какие memory/research паттерны стоит перенять из `Math_Hypothese_AutoCheck_Witch_Agents/`?
5. Какие data contracts и протоколы нужны между root и подпроектами?
6. Какие инструменты, hosted tools и MCP servers стоит использовать на первом этапе?
7. Как организовать разработку так, чтобы она с самого начала была test-first и paper-grade traceable?
8. Как организовать hierarchical departments, call graph и code-enforced visibility?

## Research workstreams

### Workstream A - Official framework decision

Нужно выбрать именно официальный OpenAI стек для multi-agent разработки, а не строить самодельный runtime без опоры на официальные primitives.

### Workstream B - Root/subproject boundary

Нужно зафиксировать не только организационную, но и техническую границу:

- root управляет;
- подпроекты исполняют;
- root хранит только глобальную память;
- подпроекты хранят собственную рабочую память локально.

### Workstream C - Reference extraction from local projects

Нужно вынуть из локальных проектов не их domain-specific содержимое, а **reusable contracts**:

- из `CayleyPy_Pancake/` - runner/CLI/artifact/UX patterns;
- из `Math_Hypothese_AutoCheck_Witch_Agents/` - docs-first memory and analysis patterns.

### Workstream D - Tooling and MCP stack

Нужно определить минимальный, но сильный стек:

- что даёт сам OpenAI platform;
- что нужно как local/shared MCP;
- что лучше реализовать как custom bridge;
- какие подключения следует отложить.

### Workstream E - TDD implementation program

Нужно разбить реализацию на итерации, где каждая новая возможность сначала описывается контрактом и тестами.

## Evidence collected

### From official OpenAI docs

Исследование официальной документации показало:

- для multi-agent orchestration на Python лучше всего подходит [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/);
- OpenAI прямо поддерживает orchestration patterns `agents as tools` и `handoffs` в [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/);
- tooling layer строится вокруг Responses API и hosted tools, включая web search, function tools и remote MCP, см. [Using tools](https://platform.openai.com/docs/guides/tools);
- remote MCP поддерживается официально, но требует отдельной trust/approval/logging discipline, см. [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp);
- tracing и run observability уже есть в SDK, см. [Tracing](https://openai.github.io/openai-agents-python/tracing/).

### From `CayleyPy_Pancake/`

Read-only exploration показала, что как engineering reference особенно ценны:

- единый operational CLI;
- отдельный experiment dispatcher;
- reproducibility runner для best-known modes;
- строгая дисциплина артефактов исследований;
- resumable research loop;
- operator/user notifications;
- явная test stratification.

### From `Math_Hypothese_AutoCheck_Witch_Agents/`

Read-only exploration показала, что как scientific-memory reference особенно ценны:

- docs-first memory;
- inbox -> processed -> cards -> reports pipeline;
- локальные atomic knowledge units;
- restricted multimodel analysis;
- separation между local working memory и export-to-root summary.

### From current root scaffold

Read-only аудит root scaffold подтвердил:

- текущий `workspace_orchestrator/` годится как bootstrap;
- но ещё нет исполнимых multi-agent contracts;
- `delegate` пока является subprocess-wrapper, а не настоящим root orchestration runtime;
- следующая техническая фаза должна начинаться с contracts/router/delegation/handoff/logging и TDD.

## Revised design direction

После исследования направление уточнено так:

1. **Framework choice**: используем `OpenAI Agents SDK` + `Responses API` как официальный базовый стек.
2. **Root runtime style**: root orchestration делаем code-first, с явными схемами и structured outputs.
3. **Agent pattern**:
   - внутри root team комбинируем manager-style orchestration и handoffs;
   - внутри подпроектов допускаем локальные manager/specialist teams по их правилам.
4. **Tool strategy**:
   - для web/papers research сначала опираемся на hosted web/tool layer и локальные adapters;
   - внешние remote MCP включаем выборочно и только с approval/logging policy.
5. **Submission policy**:
   - Kaggle submission logic остаётся внутри подпроектов;
   - root вызывает её по контракту и пишет trace/log summary.
6. **Traceability**:
   - root logs + Agents SDK tracing + subproject-local reports должны образовать восстанавливаемую цепочку решений.
7. **Organization model**:
   - root и subproject teams строятся как department-based hierarchies;
   - heads mediate cross-department coordination;
   - shared service agents используются как bounded callable specialists;
   - ACL и visibility model являются частью core runtime.

## Proposed phases after approval

### Phase A - Architecture freeze

Согласовать:

- framework decision;
- recommended team topology;
- hierarchical department model;
- communication protocols;
- access and visibility policy;
- tool/MCP stack;
- approval gates.

### Phase B - TDD root contracts

Сначала написать тесты и модели для:

- `TaskRequest`
- `RoutingDecision`
- `HandoffPackage`
- `DelegationResult`
- `EscalationRequest`
- `RunTrace`

### Phase C - Root runtime bootstrap

Реализовать:

- router;
- handoff builder;
- delegation runtime;
- result ingestion;
- root logging helpers;
- root-owned run directories.

### Phase D - OpenAI Agents SDK integration

Подключить:

- root team;
- baseline local team adapters;
- sessions/tracing;
- guarded tool use.

### Phase E - Domain bridges

Построить:

- `kaggle-bridge`
- `papers-bridge`

Сначала как contract-driven adapters, потом как production-grade integrations.

### Phase F - End-to-end dry run

Проверить без риска для real competition:

- intake -> routing -> handoff -> local dry run -> result ingestion -> root summary.

## Approval gates for discussion

Перед переходом к детальному coding желательно утвердить:

1. Сколько активных ролей должно быть в root team на v1.
2. Сколько активных ролей должно быть в subproject team на v1.
3. Нужен ли user approval перед реальным `submit` на Kaggle в первой production-версии.
4. Какие remote MCP connections считаются достаточно trusted для первой итерации.
5. Должен ли root team уметь создавать новый подпроект автоматически или сначала только через явный approval/user checkpoint.
6. Утверждаем ли department-based structure как target v1.5:
   - 25 root agents;
   - 33 subproject agents.
7. Какие shared service agents должны быть callable напрямую по всему department graph.

## Exit criterion for this phase

Текущая исследовательско-архитектурная фаза считается успешно завершённой, когда:

- framework decision зафиксирован;
- topology/protocol docs зафиксированы;
- MCP/tool strategy уточнена;
- TDD implementation plan зафиксирован;
- пользователь подтвердил ключевые архитектурные решения.
