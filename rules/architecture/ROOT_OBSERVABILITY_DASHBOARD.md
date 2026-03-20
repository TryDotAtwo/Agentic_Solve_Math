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
- `workspace_orchestrator/dashboard_assets/app_v3.js`

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

---

## 2026-03-20 topology and chat refinement

The next UX pass removed the remaining "third-card bridge" feeling and made the page read like an operator console instead of a visual demo.

### Topology stage

- Keep one full-width stage instead of three adjacent graph/bridge cards.
- Render:
  - root circular graph on the left;
  - active subproject circular graph on the right;
  - cross-team relation as a direct line between the participating agents.
- Keep graph metadata above the stage in a compact toolbar rather than inside a large central card.

### Dialogue monitor

- `Dialogue Trace` now sits directly under the topology stage in the document flow.
- The dialogue surface is explicitly admin-style:
  - thread list on the left;
  - selected conversation on the right;
  - chat-like event bubbles for `message`, `handoff`, and `tool`.
- The operator remains read-only, but can inspect the runtime more like a monitored communications system.

### Layout rationale

- The operator should first understand the active teams and their link.
- The next natural question is "what are they saying to each other?", so dialogue must come immediately after topology.
- Supporting panels such as inspector, live activity, and mission control can come afterward without interrupting the main story of the run.

### Verification delta

- `tests/test_dashboard_server.py` asserts the new topology and dialogue asset hooks.
- `tests/test_dashboard.py` continues to verify that snapshot data provides the bridge and dialogue payloads required by the UI.

---

## 2026-03-20 premium route-focus upgrade

The premium UX pass connected the two strongest dashboard surfaces:

- topology;
- dialogue.

### New behavior

- Selecting a dialogue thread now drives a route-focus state.
- The topology stage shows a compact focus summary card above the graphs.
- Same-team dialogue highlights a direct route inside the corresponding graph.
- Cross-team dialogue intensifies the root-to-subproject bridge.
- The participating source and target agents receive visual node emphasis.

### Dialogue monitor implications

- The thread list now distinguishes cross-team coordination more clearly.
- The operator can move from a conversation to the exact route on the graph without mentally reconstructing the path.
- This keeps the dashboard read-only while making it feel far more "live".

### Verification delta

- `tests/test_dashboard_server.py` now checks for:
  - `topology-focus`
  - `buildDialogueFocusState`
- Full root dashboard tests continue to pass after the interaction upgrade.

---

## 2026-03-20 live observability upgrade

The dashboard was upgraded from a mostly archival root-only surface into a live dual-scope operator console.

### New root-owned observability sources

- `.agent_workspace/runtime/root_runtime_events.jsonl`
- richer `.agent_workspace/runtime/root_runtime_status.json`

### Newly exposed operator surfaces

1. `Execution Pulse`
   - current runtime status;
   - active scope;
   - active project;
   - current phase;
   - latest recorded event.
2. `Root Graph`
   - root hierarchy and callable links.
3. `Active Subproject Graph`
   - focused subproject team topology derived from the active or latest run context.
4. `Live Activity`
   - ordered runtime event feed.
5. `Dialogue Trace`
   - operator-visible excerpts from:
     - agent messages;
     - handoffs;
     - tool-mediated exchanges.

### Runtime instrumentation model

The live runtime now records root-owned events for:

- root session start and completion;
- subproject session start and completion;
- handoff package creation;
- milestone recording;
- private memory notes;
- historian notes;
- subproject result recording;
- streamed agent/tool/handoff/message events when the provider runtime exposes them.

### Boundary guarantee

The dashboard still respects the workspace invariant:

- root reads only root-owned runtime state and root-discoverable subproject topology;
- it does not become a write-channel into subprojects;
- it does not bypass ACL by exposing hidden writable surfaces outside the owning agent dossiers.

---

## 2026-03-20 visual refinement update

The observability console was refined after the operator reported that the newer graph layout had lost the stronger visual form of the previous version.

### Decisions

1. Restore the radial command-stage graph geometry for both:
   - the root team;
   - the active subproject team.
2. Keep the newer live observability surfaces:
   - execution pulse;
   - dialogue trace;
   - live activity;
   - agent inspector;
   - milestone stream.
3. Move both graphs back to full-width stage panels so the operator can read hierarchy and call links without the layout collapsing.

### Resulting UX intent

- graph first, then explanation;
- root team and active subproject team should both feel like command stages rather than small embedded cards;
- the operator should be able to follow:
  - who is active;
  - which team is active;
  - what the last visible exchange was;
  - where the next milestone came from.

---

## 2026-03-20 layout and dialogue UX refinement

Another operator pass highlighted that the visual language of the graphs was already strong, but the page composition still made the dashboard feel oversized and harder to scan than necessary.

### Refinements

1. Introduce a single `Topology Stage` panel:
   - root graph on the left;
   - active subproject graph on the right;
   - a center bridge rail that explains the current cross-team handoff relationship.
2. Reduce visual scale:
   - smaller hero;
   - denser cards and headings;
   - shorter graph stages.
3. Replace the previous dialogue wall with a split-view console:
   - filter chips;
   - compact event list;
   - detail pane for the selected exchange.

### UX intent

- two graphs should be visible at once without forcing long scrolling;
- the relationship between root orchestration and the active subproject should be explicit;
- dialogues should be browsable like an operator console, not like a stack of oversized cards.
