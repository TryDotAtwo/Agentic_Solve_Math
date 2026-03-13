# Documentation Index

## Корневые документы

- `README.md` — обзор workspace и роль корня.
- `AGENTS.md` — корневой контракт агента.
- `PROJECT_MAP.md` — карта ролей и маршрутизации между проектами.
- `RESEARCH_SURVEY.md` — подробный аудит обоих проектов.
- `USER_PROMPTS_LOG.md` — полный журнал пользовательских постановок.
- `AGENT_ACTIVITY_LOG_SPEC.md` — стандарт логирования действий агента.
- `RESEARCH_JOURNAL.md` — хронологический журнал исследований workspace.
- `BASELINE_INTAKE_SPEC.md` — спецификация intake через корневой `kaggle_intake/`.
- `KAGGLE_AUTONOMOUS_WORKFLOW.md` — pipeline автономной работы по Kaggle-задаче.
- `SOURCE_COLLECTION_POLICY.md` — политика сбора источников и внешних материалов.
- `DOCUMENTATION_STANDARDS.md` — стандарт структуры документов и статусов.
- `EXPERIMENT_LOGGING_STANDARD.md` — стандарт логирования экспериментов.
- `MATH_RESEARCH_WORKFLOW.md` — корневой math research workflow.
- `KAGGLE_TOPICS_ARCHIVE.md` — архив и индекс разобранных Kaggle-тем.
- `AGENT_INTERACTIONS_LOG.md` — лог коммуникации и координации между субагентами.

## Корневой intake

- `kaggle_intake/README.md` — назначение корневой intake-папки.
- `kaggle_intake/_TEMPLATE_KAGGLE_INPUT.md` — шаблон входного markdown-файла.

## Корневые Cursor rules

- `.cursor/rules/root-core-memory.mdc`
- `.cursor/rules/root-documentation-sync.mdc`
- `.cursor/rules/root-baseline-intake.mdc`
- `.cursor/rules/root-kaggle-research.mdc`
- `.cursor/rules/root-math-research.mdc`

## Ключевые документы проекта `Math_Hypothese_AutoCheck_Witch_Agents/`

- `Math_Hypothese_AutoCheck_Witch_Agents/README.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/index.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/workflow.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/inbox/README.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/docs/models/README.md`
- `Math_Hypothese_AutoCheck_Witch_Agents/AGENTS.md`

## Ключевые документы проекта `CayleyPy_Pancake/`

- `CayleyPy_Pancake/README.md`
- `CayleyPy_Pancake/docs/00_AGENT_NAVIGATION.md`
- `CayleyPy_Pancake/docs/01_PROJECT_OVERVIEW.md`
- `CayleyPy_Pancake/docs/02_HISTORY_CHANGES.md`
- `CayleyPy_Pancake/docs/03_HYPOTHESES.md`
- `CayleyPy_Pancake/docs/04_RESULTS.md`
- `CayleyPy_Pancake/docs/08_ANALYSIS.md`
- `CayleyPy_Pancake/baseline/README.md`

## Ключевые entry points проекта `CayleyPy_Pancake/`

- `CayleyPy_Pancake/main.py`
- `CayleyPy_Pancake/run_best.py`
- `CayleyPy_Pancake/run_experiment.py`
- `CayleyPy_Pancake/scripts/runners/run_research.py`

## Ключевые reusable ideas

- Память и карточки знаний: `Math_Hypothese_AutoCheck_Witch_Agents/`
- Мультимодельный анализ: `Math_Hypothese_AutoCheck_Witch_Agents/`
- Engineering experiment loop: `CayleyPy_Pancake/`
- Hypothesis/result/log discipline: `CayleyPy_Pancake/`

## Сначала читать новому агенту

1. `README.md`
2. `AGENTS.md`
3. `PROJECT_MAP.md`
4. `RESEARCH_SURVEY.md`
5. `USER_PROMPTS_LOG.md`
6. профильные документы внутри нужного дочернего проекта
