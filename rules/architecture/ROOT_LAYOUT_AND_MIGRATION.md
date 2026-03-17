# Root Layout And Migration

## Цель

Зафиксировать текущую схему очистки корня и переноса root-level markdown в `rules/`.

## Target Root Layout

- `README.md`
- `AGENTS.md`
- `main.py`
- `kaggle_intake/`
- `rules/`
- `workspace_orchestrator/`
- папки подпроектов

## Canonical Locations

- карты и индексы -> `rules/core/`
- workflow -> `rules/workflows/`
- стандарты -> `rules/standards/`
- registry -> `rules/registry/`
- root logs -> `rules/logs/`
- архитектурные спецификации -> `rules/architecture/`

## Compatibility Strategy

Если файловая среда временно не позволяет физически удалить старые root duplicates:

- canonical copy всё равно живёт в `rules/`;
- root duplicate считается compatibility shim;
- новые изменения вносятся только в канонический файл под `rules/`.

## Migration Warning

Исторические документы могут ссылаться на прежние пути. При конфликте canonical считается путь под `rules/`.
