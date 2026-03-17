# Root Restructure Plan

## Цель

Сделать корень workspace минимальным и читаемым:

- один root launcher;
- один root contract;
- одна папка `rules/` для root-level документации и памяти;
- никаких смешанных предметных документов рядом с подпроектами.

## Что должно остаться в корне

- `main.py`
- `AGENTS.md`
- `README.md`
- `kaggle_intake/`
- `rules/`
- `workspace_orchestrator/`
- папки подпроектов

## Что переносится в `rules/`

### `rules/core/`

- `PROJECT_MAP.md`
- `RESEARCH_SURVEY.md`
- `DOCUMENTATION_INDEX.md`

### `rules/workflows/`

- `BASELINE_INTAKE_SPEC.md`
- `KAGGLE_AUTONOMOUS_WORKFLOW.md`
- `MATH_RESEARCH_WORKFLOW.md`
- `SOURCE_COLLECTION_POLICY.md`

### `rules/standards/`

- `AGENT_ACTIVITY_LOG_SPEC.md`
- `DOCUMENTATION_STANDARDS.md`
- `EXPERIMENT_LOGGING_STANDARD.md`
- `SUBAGENT_STANDARD_PROMPT.md`

### `rules/registry/`

- `KAGGLE_TOPICS_ARCHIVE.md`

### `rules/logs/`

- `USER_PROMPTS_LOG.md`
- `RESEARCH_JOURNAL.md`
- `AGENT_INTERACTIONS_LOG.md`

## Почему это правильно

- root docs больше не пересекаются визуально с подпроектами;
- корень становится похож на control plane, а не на третью предметную лабораторию;
- журналы, стандарты и архитектурные заметки получают ясную иерархию;
- подпроекты остаются изолированными и не тонут в root-level markdown.

## Migration Risks

- старые ссылки внутри некоторых исторических файлов могут указывать на старые root paths;
- часть подпроектных документов может по-прежнему ссылаться на старый плоский root layout;
- исторические формулировки `ML in Math` потребуют аккуратной интерпретации.

## Mitigations

- обновить root README и AGENTS;
- обновить root navigation docs;
- не трогать локальные документы подпроектов без отдельного задания;
- фиксировать архитектурный boundary как главный инвариант.
