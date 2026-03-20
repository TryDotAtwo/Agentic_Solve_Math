# Root Observability Dashboard

## Назначение

Этот документ фиксирует root-level browser interface для наблюдения за работой мультиагентной системы.

Dashboard относится только к **корневому orchestration layer** и не подменяет локальные UI или логи подпроектов.

## Цели

- дать пользователю приятную и понятную browser surface для наблюдения за ходом работ;
- показывать только canonical root-managed sources of truth;
- не нарушать изоляцию подпроектов;
- сохранять научную трассируемость и воспроизводимость.

## Канонические источники данных

Dashboard читает только root-managed данные:

- `.agent_workspace/runs/<run_id>/`
- `.agent_workspace/sessions/*.sqlite`
- `.agent_workspace/runtime/root_runtime_status.json`
- `rules/logs/RESEARCH_JOURNAL.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`
- `rules/logs/USER_PROMPTS_LOG.md`
- root workspace snapshot
- root organization/runtime specs
- latest root intake file

Dashboard не должен напрямую читать внутренние артефакты подпроектов вне тех данных, которые уже отражены в root-owned handoff/run artifacts.

## Реализация

### Backend

- `workspace_orchestrator/dashboard.py` — агрегатор canonical snapshot payload.
- `workspace_orchestrator/dashboard_server.py` — local HTTP server и JSON endpoints.
- `workspace_orchestrator/runtime_state.py` — root runtime status file для live observability.

### Frontend

Static assets живут в:

- `workspace_orchestrator/dashboard_assets/index.html`
- `workspace_orchestrator/dashboard_assets/app.css`
- `workspace_orchestrator/dashboard_assets/app.js`

Frontend обновляет snapshot polling-механизмом и не требует внешних JS/CSS dependencies.

## UI sections

Dashboard должен показывать:

1. `Mission Control`
   - bootstrap configured / missing;
   - provider route;
   - SDK availability;
   - latest root runtime status.
2. `Root Team`
   - manager;
   - departments;
   - shared service agents;
   - preferred model distribution.
3. `Run Deck`
   - recent root-owned runs;
   - lifecycle status;
   - execution/result snapshots;
   - canonical artifacts and events.
4. `Workspace Surface`
   - root paths;
   - visible subprojects;
   - latest intake;
   - session storage.
5. `Research Memory`
   - research journal;
   - agent interactions;
   - user prompts.

## Root runtime status

Live root runtime теперь обязан записывать high-level статус в:

- `.agent_workspace/runtime/root_runtime_status.json`

Минимальные поля:

- `status`
- `team_id`
- `entry_agent_id`
- `model`
- `session_id`
- `started_at`
- `updated_at`
- `finished_at`
- `intake_file`
- `prompt_excerpt`
- `final_output_excerpt`
- `error`

Это нужно для live observation без чтения внутренних SDK объектов.

## Запуск

Standalone запуск dashboard:

```bash
python main.py dashboard
```

Snapshot-only режим:

```bash
python main.py dashboard --json
```

Основной операторский режим:

1. Запустить `python main.py`.
2. Дождаться печати `dashboard_url` в терминале.
3. Наблюдать root orchestration cycle и dashboard внутри одного operator session.
4. Для остановки нажать `Ctrl+C` в том же терминале.

Раздельный режим всё ещё поддерживается:

1. Запустить `python main.py dashboard`, если нужен только UI.
2. Отдельно запускать служебные root-команды при необходимости.

## Границы и безопасность

- dashboard не показывает секреты из `.env`;
- dashboard не мутирует подпроекты;
- dashboard читает только root-owned или root-discoverable state;
- dashboard не должен становиться новым каналом обхода ACL.

## Verification baseline

Минимальная TDD-проверка должна покрывать:

- snapshot aggregation;
- HTTP serving;
- CLI dashboard surface;
- root runtime status recording.

---

## 2026-03-20 redesign update

The dashboard moved from a card-only debug surface to a structured observability console.

### New operator-facing sections

1. `Team Graph`
   - root agents are rendered as graph vertices;
   - hierarchy edges show the formal command structure;
   - selected-agent overlays show callable links from the ACL graph.
2. `Agent Inspector`
   - exposes one selected root agent at a time;
   - shows preferred model, allowed tools, writable surfaces, callable peers;
   - surfaces excerpts from the agent's private files.
3. `Milestone Stream`
   - aggregates department-head reports into user-facing milestones;
   - gives the operator a concise story of progress without reading raw logs.

### Private profile substrate

Each root agent now has a dedicated private profile root under:

- `.agent_workspace/agent_profiles/root/<department>/<agent>/`

Materialized files:

- `memory.md`
- `instructions.md`
- `rules.md`
- `reports.md`

The owner agent can write to its own `memory.md` and `reports.md`, while peer agents are blocked by visibility and write-scope policy.

### Runtime implications

- live runtime tools now include a private memory append tool for every agent;
- department heads additionally receive a milestone-reporting tool;
- dashboard aggregation reads the canonical profile files instead of inventing a second UI-only state model.

### Verification delta

The redesign remains covered by tests for:

- agent profile materialization;
- owner-only private memory writes;
- milestone aggregation into dashboard snapshots;
- dashboard HTTP serving of the active frontend bundle;
- department-head runtime tooling.
