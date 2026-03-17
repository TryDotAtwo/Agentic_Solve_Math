# Kaggle Autonomous Workflow

## Цель

Этот workflow описывает, как **root meta-orchestrator** должен запускать новый цикл работы по Kaggle-задаче, не ломая автономность подпроектов.

## Базовый инвариант

- intake всегда начинается в `kaggle_intake/`;
- root-level агент подготавливает только глобальный контекст и маршрутизацию;
- предметная работа затем уходит в изолированный Kaggle подпроект;
- математическая ветка при необходимости подключается как отдельный подпроектный или межпроектный трек;
- в root поднимаются только summaries, registry updates, prompts и межпроектные решения.

## Фаза 1. Root Intake

1. Прочитать intake-файл из `kaggle_intake/`.
2. Извлечь:
   - competition links;
   - official slug;
   - дополнительные ссылки;
   - пользовательские приоритеты;
   - ограничения по времени, compute, внешним данным.
3. Обновить root-level память:
   - `rules/logs/USER_PROMPTS_LOG.md`
   - `rules/logs/RESEARCH_JOURNAL.md`
   - при необходимости `rules/registry/KAGGLE_TOPICS_ARCHIVE.md`

## Фаза 2. Root Problem Framing

Root agent обязан собрать минимальный handoff package до входа в подпроект:

1. подтвердить competition slug и базовый контракт задачи;
2. зафиксировать:
   - цель;
   - metric;
   - данные;
   - submission format;
   - ограничения;
   - внешние источники, которые уже найдены;
3. определить:
   - использовать существующий подпроект;
   - создать новый подпроект;
   - подключить math-support ветку или нет.

Если часть информации не подтверждена, root явно маркирует это как `needs verification`.

## Фаза 3. Source Of Truth Policy

Перед любыми инженерными гипотезами агент или назначенный subproject team обязан:

1. скачать официальные Kaggle-файлы;
2. проверить `sample_submission.csv`, `test.csv` и все специальные схемы данных;
3. зафиксировать, что именно официальные Kaggle-файлы являются источником правды по интерфейсам;
4. отдельно записать все расхождения между локальными предположениями и реальным контрактом.

Это правило важнее локальных догадок, README и черновых генераторов.

## Фаза 4. Handoff To Isolated Subproject

После framing root agent формирует и передаёт в подпроект:

- intake summary;
- curated links;
- known constraints;
- список вопросов на проверку;
- список ожидаемых первых артефактов.

Дальше локальная команда подпроекта сама организует:

- baseline building;
- parsing competition files;
- search for notebooks, repos and papers;
- experiments;
- autosubmit setup;
- local documentation updates.

## Фаза 5. Local Research Loop Inside Subproject

Внутри подпроекта ожидается цикл:

1. hypothesis or baseline idea;
2. verification plan;
3. run or theoretical analysis;
4. local docs and artifacts update;
5. local status decision.

Root не должен дублировать этот локальный цикл у себя.

## Фаза 6. Return To Root

Из подпроекта вверх должны возвращаться только:

- status summary;
- best current result;
- major risks;
- ссылки на canonical local docs;
- requests for escalation;
- cross-project insights.

Root после этого обновляет:

- `rules/logs/RESEARCH_JOURNAL.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`
- `rules/registry/KAGGLE_TOPICS_ARCHIVE.md`
- при необходимости `rules/core/DOCUMENTATION_INDEX.md`

## Критерии хорошей root-level автономной работы

Хорошая root orchestration по Kaggle означает, что система:

- не смешивает intake и локальную реализацию;
- умеет создавать изолированные подпроекты;
- не теряет конкурсный контракт и реальные Kaggle файлы;
- отделяет root summaries от local working memory;
- ведёт научно воспроизводимую историю решений.
