# Root Restructure And Invariants

## Core invariant

Каждый подпроект — самодостаточная и изолированная система.

Корень:

- не является общим execution sandbox;
- не подменяет локальные project docs;
- не смешивает локальные команды;
- не хранит локальные heuristics как часть общей каши.

## Why restructure now

По результатам обзора:

- корневые markdown-файлы были рассыпаны по плоскому слою;
- пути и контракты частично устарели;
- в repo сохранились исторические ссылки на `ML in Math/`;
- root launcher был фактически competition-specific wrapper.

## Decision

Вводится canonical root-docs tree `rules/`.

Корень оставляет только bootstrap и compatibility файлы.

## Compatibility layer

Пока в корне сохраняются:

- `RESEARCH_JOURNAL.md`
- `EXPERIMENT_LOGGING_STANDARD.md`

Причина:

- на них уже ссылаются локальные документы подпроектов.

## Risks

- stale references in historical logs;
- stale references inside local subprojects;
- old terminology (`ML in Math`) in legacy docs;
- риск перепутать root orchestration и local execution во время дальнейшего кодинга.

## Mitigation

- canonical paths фиксируются в `rules/core/DOCUMENTATION_INDEX.md`;
- новые docs используют только новые пути;
- migration notes сохраняются в журналах;
- локальные path updates будут делаться через локальные команды подпроектов.
