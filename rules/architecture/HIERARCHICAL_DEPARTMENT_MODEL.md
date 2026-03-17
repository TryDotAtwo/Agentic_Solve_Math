# Hierarchical Department Model

## Goal

Зафиксировать уже не упрощённую, а **масштабную иерархическую структуру** root team и subproject teams:

- с департаментами;
- с начальниками департаментов;
- с сотрудниками;
- с shared service agents;
- с жёсткой иерархией коммуникации и изменения правил.

## Core principle

Нам нужна не просто "группа ролей", а организационная система уровня research lab:

- root team проектирует, координирует, улучшает команды и решает конфликты;
- subproject teams решают предметные задачи подпроекта;
- обе стороны имеют внутреннюю иерархию;
- видимость, права и коммуникации ограничиваются не только промптом, но и кодом.

## Executive rule

- Root Orchestrator общается только с главами департаментов.
- Начальники департаментов координируют междепартаментное взаимодействие.
- Сотрудники по умолчанию работают внутри своего департамента.
- Shared service agents могут вызываться напрямую многими ролями, если это разрешено ACL.
- Подпроектные команды не могут менять root, но могут отправлять formal change requests.

## Root organization

## Executive layer

### `Root Orchestrator`

Роль:

- принимает intake;
- запускает root team;
- назначает задачи главам департаментов;
- меняет глобальные цели, контекст и жёсткие root-level правила;
- утверждает критичные restructuring decisions.

Он не должен вести обычную мелкую операционную работу департаментов.

## Root departments

Рекомендуемая структура root v1.5:

- 1 orchestrator
- 8 departments
- в каждом департаменте: 1 head + 2 staff agents

Итого: **25 root agents**.

### Department 01 - Intake and Orchestration

- `Head of Intake and Orchestration`
- `Intake Analyst`
- `Context Packager`

Mission:

- разобрать новый intake;
- извлечь входной контекст;
- собрать стартовые handoff packages;
- инициировать запуск нужных департаментов.

### Department 02 - Research Intelligence

- `Head of Research Intelligence`
- `Global Searcher`
- `Paper Scout`

Mission:

- искать информацию в интернете;
- искать статьи, репозитории, ноутбуки, baseline ideas;
- обслуживать cross-department search requests.

Shared service note:

- `Global Searcher` и `Paper Scout` являются shared service agents и могут вызываться многими департаментами напрямую.

### Department 03 - Architecture and Capability

- `Head of Architecture and Capability`
- `Capability Designer`
- `Rule Engineer`

Mission:

- проектировать team topology;
- проектировать контракты, rules, manifests;
- предлагать изменения к структуре команд и правам.

### Department 04 - Tooling and MCP Ops

- `Head of Tooling and MCP Ops`
- `Tool Integrator`
- `Access Operator`

Mission:

- подключать и сопровождать tools и MCP;
- вести policy по разрешениям;
- обслуживать runtime integrations и bridges.

### Department 05 - Cross-project Analysis

- `Head of Cross-project Analysis`
- `Benchmark Analyst`
- `Pattern Synthesizer`

Mission:

- сравнивать подпроекты;
- извлекать reusable patterns;
- готовить мета-выводы и оценки эффективности команд.

### Department 06 - Editorial and History

- `Head of Editorial and History`
- `History Scribe`
- `Article Drafter`

Mission:

- вести историю изменений;
- вести paper-grade evidence trail;
- сразу собирать заготовки статьи и narrative.

Shared service note:

- `History Scribe` является shared service agent, которого другие роли могут вызывать напрямую для записи значимых действий и решений.

### Department 07 - Audit and Compliance

- `Head of Audit and Compliance`
- `Access Auditor`
- `Result Verifier`

Mission:

- проверять корректность выводов;
- проверять соблюдение ACL/rules;
- быть независимым департаментом сомнений, конфликтов и проверки.

Communication note:

- любой head может обратиться в audit department;
- сотрудники по умолчанию эскалируют в audit через своего head, кроме explicitly shared audit routes.

### Department 08 - Organization Evolution

- `Head of Organization Evolution`
- `Workforce Designer`
- `Training Curator`

Mission:

- улучшать структуру root team;
- проектировать новые департаменты и роли;
- готовить изменения шаблонов для будущих subproject teams.

## Subproject organization template

## Executive layer

### `Subproject Commander`

Роль:

- управляет всей локальной командой подпроекта;
- получает handoff package от root;
- назначает задачи heads локальных департаментов;
- утверждает локальные цели и приоритеты;
- отправляет `DelegationResult` и `EscalationRequest` в root.

## Subproject departments

Рекомендуемая структура subproject v1.5:

- 1 subproject commander
- 8 departments
- в каждом департаменте: 1 head + 3 staff agents

Итого: **33 subproject agents**.

### Department 01 - Source Intelligence

- `Head of Source Intelligence`
- `Web Researcher`
- `Paper Researcher`
- `Baseline Scout`

### Department 02 - Problem Analysis

- `Head of Problem Analysis`
- `Hypothesis Analyst`
- `Formal Analyst`
- `Failure Analyst`

### Department 03 - Data and Parsing

- `Head of Data and Parsing`
- `Dataset Parser`
- `Schema Validator`
- `Artifact Indexer`

### Department 04 - Experimentation

- `Head of Experimentation`
- `Experiment Planner`
- `Runner Operator`
- `Benchmark Recorder`

### Department 05 - Solver Engineering

- `Head of Solver Engineering`
- `Search Engineer`
- `Model Engineer`
- `Pipeline Integrator`

### Department 06 - Evaluation and Submission

- `Head of Evaluation and Submission`
- `Metric Analyst`
- `Submission Operator`
- `Leaderboard Monitor`

### Department 07 - Editorial and History

- `Head of Editorial and History`
- `Local Historian`
- `Report Drafter`
- `Evidence Curator`

### Department 08 - Audit and Validation

- `Head of Audit and Validation`
- `Rule Auditor`
- `Result Validator`
- `Access Checker`

## Hierarchy of interaction

## Allowed by default

### Root Orchestrator

Can talk to:

- all root department heads

Cannot talk directly to:

- ordinary staff, except emergency or explicit override mode

### Department heads

Can talk to:

- root/subproject commander
- heads of other departments
- their own staff
- shared service agents
- audit head

### Staff agents

Can talk to:

- their own head
- staff of the same department
- explicitly shared service agents

Cannot talk by default to:

- root orchestrator / subproject commander
- heads of other departments
- arbitrary staff in other departments

## Shared service exception

Следующие типы агентов могут вызываться напрямую многими ролями при наличии ACL:

- search agents;
- paper lookup agents;
- history agents;
- selected audit utility agents;
- selected tooling utility agents.

Это нужно, чтобы не душить скорость работы, но при этом не ломать иерархию.

## Rule mutation authority

### Root hard rules

Меняются только:

- `Root Orchestrator`
- or explicit root governance flow

### Department local rules

Могут изменяться:

- head соответствующего департамента

Но только:

- внутри namespace своего департамента;
- без нарушения root hard rules;
- без расширения прав за пределы разрешённой policy envelope.

### Subproject local rules

Могут изменяться:

- `Subproject Commander`
- heads локальных департаментов в рамках своих областей

Но они:

- не могут менять root hard rules;
- не могут менять соседние подпроекты;
- не могут расширять доступ к root beyond granted envelope.

## Folder structure

Для удобства и будущей кодогенерации у каждого департамента должна быть своя папка.

Текущий root organization tree:

- `rules/organization/root_command/`
- `rules/organization/root_departments/<department>/`
- `rules/organization/subproject_template_departments/<department>/`

В дальнейшем в каждой папке департамента должны жить:

- `README.md`
- `AGENTS.md`
- `ACCESS_POLICY.md`
- `ROLE_MATRIX.md`
- `MANIFEST_TEMPLATE.json`
- `TASK_TEMPLATES.md`

На текущем этапе мы фиксируем эту структуру как canonical design target и заводим папки с `README.md`.

## Recommendation

Эта hierarchical model должна стать **целевой организационной моделью**, а предыдущая упрощённая topology из `TEAM_TOPOLOGY_AND_RUNTIME_PROTOCOLS.md` должна рассматриваться как baseline/minimal fallback, а не как конечная форма системы.
