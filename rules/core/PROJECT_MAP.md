# Project Map

## Главный принцип

Workspace устроен как **двухуровневая мультиагентная система**:

1. **Root layer** - meta-orchestrator, который ведёт глобальные правила, память и маршрутизацию.
2. **Subproject layer** - изолированные самодостаточные подпроекты, внутри которых работают свои локальные команды агентов.

Корень не должен превращаться в третий предметный проект. Его роль - координация и synthesis.

## Layer 0 - Root Meta-Orchestrator

### Каноническое место

- `README.md`
- `AGENTS.md`
- `main.py`
- `runtime_config.toml`
- `rules/`
- `kaggle_intake/`
- `workspace_orchestrator/`

### Ответственность

- принимать новые глобальные задачи;
- сохранять пользовательские запросы и исследовательскую историю;
- определять, в какой подпроект маршрутизировать работу;
- создавать новые подпроекты для новых Kaggle-соревнований;
- координировать несколько подпроектов одновременно;
- агрегировать результаты вверх до уровня статьи, программы исследований и общих архитектурных решений.

### Что root не должен делать

- хранить локальную память подпроекта вместо самого подпроекта;
- редактировать внутренние документы и код подпроекта напрямую;
- унифицировать локальные workflows подпроектов ценой потери их автономности;
- смешивать локальные артефакты нескольких подпроектов в один общий архив.

## Layer 1 - Isolated Subproject Multi-Agent Teams

Каждый подпроект должен трактоваться как локально автономная команда со своей памятью, правилами и инструментами.

### Активные канонические узлы

| Subproject | Role | Local autonomy | Что экспортирует в root |
|---|---|---|---|
| `CayleyPy_Pancake/` | engineering reference-проект для Kaggle solver pipelines | свои docs, runners, results, hypotheses, tests | summary лучших практик, выводы, ссылки на артефакты |
| `Math_Hypothese_AutoCheck_Witch_Agents/` | математическая research-система | свои knowledge cards, proofs, reports, models, Lean path | согласованные hypothesis summaries, риски, ссылки на canonical artifacts |
| `CayleyPy_444_Cube/` | Kaggle подпроект по C4 | свои docs, search, autosubmit, results | engineering/math summaries, статус baseline/submission |
| `CayleyPy_*` другие | отдельные Kaggle подпроекты | должны оставаться изолированными | краткий статус, основные ссылки, запросы к root |

## Routing Rules

### Если задача про root architecture, orchestration, глобальные правила, межпроектную координацию

- работать в корне;
- обновлять `rules/`;
- обновлять `main.py`, `workspace_orchestrator/` и root logs.

### Если задача про Kaggle, solver pipeline, baseline, submission, score

- выбрать или создать отдельный Kaggle подпроект;
- корень готовит intake, registry и handoff package;
- дальше локальная команда подпроекта работает внутри своей папки.

### Если задача про гипотезу, статью, доказательство, формализацию

- основной рабочий проект: `Math_Hypothese_AutoCheck_Witch_Agents/`;
- root only logs prompt, routing и межпроектные выводы.

## Root-Owned Global Documents

- `rules/logs/USER_PROMPTS_LOG.md`
- `rules/logs/RESEARCH_JOURNAL.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`
- `rules/registry/KAGGLE_TOPICS_ARCHIVE.md`
- `rules/core/DOCUMENTATION_INDEX.md`
- `rules/core/PROJECT_MAP.md`
- `rules/architecture/*.md`

## Historical Note

Некоторые старые материалы используют название `ML in Math/`. Для root-level карты канонический engineering reference-проект называется `CayleyPy_Pancake/`. Локальные подпроектные документы при этом остаются историческими артефактами и не должны переписываться без необходимости.
