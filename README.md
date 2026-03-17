# Agentic Solve Math

Корень `D:\Agentic_Solve_Math` теперь должен пониматься как **meta-layer / coordinator layer**, а не как ещё один предметный проект.

## Архитектурный инвариант

- Каждый подпроект является **самодостаточной и изолированной системой**.
- У каждого подпроекта должны быть:
  - своя локальная документация;
  - свои локальные правила;
  - свой локальный `AGENTS.md`;
  - своя собственная мультиагентная команда.
- Корень **не смешивает** локальные уровни между собой.
- Корень:
  - координирует подпроекты;
  - ведёт глобальную память и трассируемость;
  - принимает новые задачи;
  - проектирует общую архитектуру;
  - решает глобальные cross-project задачи.

## Что находится в корне

- `main.py` — единая root-level точка запуска.
- `AGENTS.md` — корневой контракт оркестратора.
- `rules/` — canonical дерево корневой документации.
- `kaggle_intake/` — canonical intake для новых Kaggle-задач.
- `workspace_orchestrator/` — код root-level orchestration scaffold.
- подпроекты `CayleyPy_*` и `Math_Hypothese_AutoCheck_Witch_Agents/`.

## Сначала читать

Перед новой содержательной сессией:

1. `README.md`
2. `AGENTS.md`
3. `rules/README.md`
4. `rules/core/PROJECT_MAP.md`
5. `rules/core/RESEARCH_SURVEY.md`
6. `rules/core/DOCUMENTATION_INDEX.md`
7. `rules/logs/USER_PROMPTS_LOG.md`
8. затем локальные документы нужного подпроекта

## Смысл папки `rules/`

`rules/` — это canonical место для корневых:

- карт и индексов;
- workflow/spec документов;
- стандартов;
- журналов и памяти оркестратора;
- архитектурных планов и design notes для следующего этапа разработки.

Подробности: `rules/README.md`.

## Статус root launcher

Сейчас `main.py` ещё сохраняет совместимость со сценарием CayleyPy-444-Cube и работает как тонкий wrapper.

Целевое состояние:

- `main.py` запускает универсальный root orchestrator;
- orchestrator читает intake, поднимает мультиагентную систему и делегирует работу в изолированные подпроекты;
- локальная реализация остаётся внутри подпроектов, а не в корне.

Подробная целевая архитектура вынесена в:

- `rules/architecture/ROOT_RESTRUCTURE_PLAN.md`
- `rules/architecture/ROOT_MULTIAGENT_ARCHITECTURE.md`
- `rules/architecture/AGENT_PROTOCOLS.md`
- `rules/architecture/KAGGLE_RESEARCH_AGENT_BLUEPRINT.md`
- `rules/architecture/MCP_SERVER_STRATEGY.md`
- `rules/architecture/IMPLEMENTATION_ROADMAP.md`

## Intake для Kaggle

Новые Kaggle-задачи поступают через `kaggle_intake/`.

Root orchestrator обязан:

1. прочитать intake-файл;
2. извлечь competition links, требования, источники и ограничения;
3. зафиксировать запрос и старт ветки исследования;
4. определить, нужен ли новый изолированный подпроект;
5. делегировать локальную работу соответствующей мультиагентной команде подпроекта;
6. сохранить глобальные выводы в корневой памяти.

См. также:

- `rules/workflows/BASELINE_INTAKE_SPEC.md`
- `rules/workflows/KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `rules/workflows/SOURCE_COLLECTION_POLICY.md`

## Подпроекты

- `CayleyPy_Pancake/` — инженерный эталон по UX, beam search, GPU-oriented solve pipeline, логированию и сабмитной дисциплине.
- `CayleyPy_444_Cube/` и другие `CayleyPy_*` — отдельные competition-specific подпроекты.
- `Math_Hypothese_AutoCheck_Witch_Agents/` — эталон memory/research architecture для математической ветки.

Главное правило: корень координирует, подпроекты реализуют.
