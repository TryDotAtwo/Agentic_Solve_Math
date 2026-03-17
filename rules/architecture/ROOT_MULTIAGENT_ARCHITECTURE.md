# Root Multiagent Architecture

## Design goal

Построить root-level мультиагентную систему, которая:

- принимает новые Kaggle и math задачи;
- координирует подпроекты;
- поддерживает scientific traceability;
- не разрушает автономию локальных project teams;
- служит основой для будущей статьи.

## Главный инвариант

Подпроект = автономная локальная система.

Это означает:

- локальная документация живёт в подпроекте;
- локальные правила живут в подпроекте;
- локальная мультиагентная команда живёт в подпроекте;
- локальные артефакты экспериментов и выводов живут в подпроекте.

Root layer не переносит эту логику в корень. Root only:

- роутит задачи;
- ведёт глобальные журналы;
- создаёт новые подпроекты;
- синтезирует межпроектные выводы;
- задаёт общие интерфейсы и standards.

## Слои системы

### Root coordination layer

Артефакты:

- `main.py`
- `rules/`
- `kaggle_intake/`

Функции:

- intake and routing;
- registry of subprojects;
- global memory;
- cross-project synthesis;
- MCP policy and shared contracts.

### Local project layer

Артефакты:

- `CayleyPy_*` subprojects
- `Math_Hypothese_AutoCheck_Witch_Agents/`

Функции:

- domain-specific research;
- local runtimes;
- local experiments;
- local docs;
- local agent teams;
- local outputs and reports.

### External tool layer

Сюда входят:

- Kaggle CLI / API;
- scholarly APIs;
- MCP servers;
- local compute and GPU runners;
- browser / fetch tooling;
- version-control and artifact storage tooling.

## Root agent roles

### Intake and Router

Отвечает за:

- чтение `kaggle_intake/`;
- определение task type;
- выбор или создание подпроекта;
- назначение локальной команды.

### Global Memory Curator

Отвечает за:

- `USER_PROMPTS_LOG.md`;
- `RESEARCH_JOURNAL.md`;
- `AGENT_INTERACTIONS_LOG.md`;
- `KAGGLE_TOPICS_ARCHIVE.md`.

### Cross-project Synthesizer

Отвечает за:

- сравнение результатов разных подпроектов;
- перенос reusable patterns на уровень общих архитектурных документов;
- подготовку материалов для статьи и общих программных решений.

### Runtime Coordinator

Отвечает за:

- top-level `main.py`;
- запуск нужного project runtime;
- согласование shared MCP stack;
- policy around shared compute, artifacts and automation.

## Runtime implication

Root `main.py` должен eventually делать только три вещи:

1. parse global command and task context;
2. select project runtime or project team;
3. launch and supervise the correct local workflow.

Root `main.py` не должен содержать domain-heavy solver logic.

## What to reuse from reference projects

### From `CayleyPy_Pancake/`

- entrypoint discipline;
- experiment loop;
- run artifacts;
- compare/evaluate/log pipeline;
- user-facing feedback quality.

### From `Math_Hypothese_AutoCheck_Witch_Agents/`

- inbox to structured memory;
- atomic cards;
- multimodel analysis;
- proof/formalization path;
- scientific reproducibility discipline.
