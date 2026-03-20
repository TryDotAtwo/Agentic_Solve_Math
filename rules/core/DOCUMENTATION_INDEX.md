# Documentation Index

## Canonical Index

Use this section as the current source of truth.

### Root Entry Points

- `../../README.md`
- `../../AGENTS.md`
- `../../main.py`
- `../../kaggle_intake/`
- `../../workspace_orchestrator/`

### Root Rules Tree

- `../README.md`
- `PROJECT_MAP.md`
- `RESEARCH_SURVEY.md`
- `../workflows/BASELINE_INTAKE_SPEC.md`
- `../workflows/KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `../workflows/MATH_RESEARCH_WORKFLOW.md`
- `../workflows/SOURCE_COLLECTION_POLICY.md`
- `../standards/SUBAGENT_STANDARD_PROMPT.md`
- `../standards/AGENT_ACTIVITY_LOG_SPEC.md`
- `../standards/DOCUMENTATION_STANDARDS.md`
- `../standards/EXPERIMENT_LOGGING_STANDARD.md`
- `../registry/KAGGLE_TOPICS_ARCHIVE.md`
- `../logs/USER_PROMPTS_LOG.md`
- `../logs/RESEARCH_JOURNAL.md`
- `../logs/AGENT_INTERACTIONS_LOG.md`
- `../architecture/ROOT_RESTRUCTURE_PLAN.md`
- `../architecture/ROOT_MULTIAGENT_ARCHITECTURE.md`
- `../architecture/AGENT_PROTOCOLS.md`
- `../architecture/KAGGLE_RESEARCH_AGENT_BLUEPRINT.md`
- `../architecture/MCP_SERVER_STRATEGY.md`
- `../architecture/IMPLEMENTATION_ROADMAP.md`
- `../architecture/RESEARCH_AND_DESIGN_PROGRAM.md`
- `../architecture/OPENAI_AGENTS_SDK_DECISION.md`
- `../architecture/TEAM_TOPOLOGY_AND_RUNTIME_PROTOCOLS.md`
- `../architecture/PHASE_2_TDD_IMPLEMENTATION_PLAN.md`
- `../architecture/HIERARCHICAL_DEPARTMENT_MODEL.md`
- `../architecture/ACCESS_CONTROL_AND_VISIBILITY_MODEL.md`
- `../architecture/ROOT_OBSERVABILITY_DASHBOARD.md`
- `../organization/README.md`
- `../organization/root_command/README.md`
- `../organization/root_departments/README.md`
- `../organization/subproject_template_departments/README.md`

### Canonical Subproject Docs

- `../../CayleyPy_Pancake/README.md`
- `../../CayleyPy_Pancake/docs/00_AGENT_NAVIGATION.md`
- `../../Math_Hypothese_AutoCheck_Witch_Agents/README.md`
- `../../Math_Hypothese_AutoCheck_Witch_Agents/AGENTS.md`
- `../../Math_Hypothese_AutoCheck_Witch_Agents/docs/index.md`
- `../../CayleyPy_444_Cube/README.md`
- `../../CayleyPy_444_Cube/docs/01_COMPETITION_OVERVIEW.md`

## Historical Notes (obsolete, ignore)

Everything below this marker is preserved only as historical migration residue. Do not use it as an operational source of truth.

## Root Bootstrap

- `README.md` — краткий обзор workspace и root-level роли.
- `AGENTS.md` — корневой контракт оркестратора.
- `main.py` — единая root-level точка запуска.
- `RESEARCH_JOURNAL.md` — живой cross-project журнал.
- `EXPERIMENT_LOGGING_STANDARD.md` — временно оставленный compatibility-standard.

## Canonical Root Docs

Canonical root docs now live in `rules/`.

Important migration note:

- use subfolders `core/`, `policies/`, `standards/`, `memory/` as the source of truth;
- in `rules/architecture/`, use numbered docs `00_` ... `06_` plus `architecture/README.md`;
- loose top-level files and extra draft directories inside `rules/` are non-canonical migration artifacts until later consolidation.

### Core

- `rules/README.md` — назначение и структура дерева `rules/`.
- `rules/core/DOCUMENTATION_INDEX.md` — этот индекс.
- `rules/core/PROJECT_MAP.md` — карта ответственности между корнем и подпроектами.
- `rules/core/RESEARCH_SURVEY.md` — исторический обзор текущего состояния repo.
- `rules/core/SUBAGENT_STANDARD_PROMPT.md` — базовый контракт субагента.

### Policies

- `rules/policies/BASELINE_INTAKE_SPEC.md` — спецификация intake через `kaggle_intake/`.
- `rules/policies/KAGGLE_AUTONOMOUS_WORKFLOW.md` — root-to-subproject workflow по Kaggle.
- `rules/policies/SOURCE_COLLECTION_POLICY.md` — политика сбора источников.

### Standards

- `rules/standards/AGENT_ACTIVITY_LOG_SPEC.md` — формат подробного activity logging.
- `rules/standards/DOCUMENTATION_STANDARDS.md` — стандарт для root-managed документации.
- `rules/standards/MATH_RESEARCH_WORKFLOW.md` — корневой math workflow.

### Memory

- `rules/memory/USER_PROMPTS_LOG.md` — журнал пользовательских промптов.
- `rules/memory/KAGGLE_TOPICS_ARCHIVE.md` — архив Kaggle тем и подпроектов.
- `rules/memory/AGENT_INTERACTIONS_LOG.md` — журнал координации между агентами.

### Architecture

- `rules/architecture/README.md` — правило каноничности architecture docs.
- `rules/architecture/00_MASTER_ROADMAP.md` — master roadmap следующего этапа.
- `rules/architecture/01_ROOT_RESTRUCTURE_AND_INVARIANTS.md` — инварианты и план перестройки корня.
- `rules/architecture/02_MULTIAGENT_SYSTEM_ARCHITECTURE.md` — целевая системная архитектура.
- `rules/architecture/03_AGENT_ROLES_AND_INTERACTION_PROTOCOL.md` — роли агентов и протоколы связи.
- `rules/architecture/04_KAGGLE_RESEARCH_PIPELINE_V2.md` — детальный Kaggle pipeline v2.
- `rules/architecture/05_MCP_SERVER_STRATEGY.md` — стратегия MCP/tooling.
- `rules/architecture/06_SCIENTIFIC_TRACEABILITY_AND_EVIDENCE.md` — модель доказательности и воспроизводимости.
- `rules/architecture/ROOT_MULTIAGENT_ARCHITECTURE.md` — компактная карта root vs local system boundaries.
- `rules/architecture/SUBPROJECT_TEAM_PROTOCOL.md` — протокол автономных локальных команд подпроектов.
- `rules/architecture/MCP_SERVER_STRATEGY.md` — практическая рекомендация по shared MCP stack и custom bridges.
- `rules/architecture/PHASE_1_EXECUTION_PLAN.md` — краткий executable plan первого этапа.
- `rules/architecture/ROOT_LAYOUT_AND_MIGRATION.md` — схема текущей миграции root markdown в `rules/`.

## Root Intake

- `kaggle_intake/README.md`
- `kaggle_intake/_TEMPLATE_KAGGLE_INPUT.md`
- `kaggle_intake/*.md` — входные файлы новых Kaggle-задач

## Root Cursor Rules

- `.cursor/rules/root-core-memory.mdc`
- `.cursor/rules/root-documentation-sync.mdc`
- `.cursor/rules/root-baseline-intake.mdc`
- `.cursor/rules/root-kaggle-research.mdc`
- `.cursor/rules/root-math-research.mdc`

## Key Local Docs: `Math_Hypothese_AutoCheck_Witch_Agents/`

- `Math_Hypothese_AutoCheck_Witch_Agents/README.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/AGENTS.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/index.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/workflow.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/inbox/README.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/models/README.md`

## Key Local Docs: `CayleyPy_Pancake/`

- `CayleyPy_Pancake/README.md`
- `CayleyPy_Pancake/docs/00_AGENT_NAVIGATION.md`
- `CayleyPy_Pancake/docs/01_PROJECT_OVERVIEW.md`
- `CayleyPy_Pancake/docs/02_HISTORY_CHANGES.md`
- `CayleyPy_Pancake/docs/03_HYPOTHESES.md`
- `CayleyPy_Pancake/docs/04_RESULTS.md`
- `CayleyPy_Pancake/docs/08_ANALYSIS.md`

## Principle

Если документ описывает глобальную координацию, маршрутизацию, память или архитектуру оркестратора, он живёт в canonical `rules/` subtree.

Если документ описывает локальную работу конкретного подпроекта, он должен жить внутри самого подпроекта.
