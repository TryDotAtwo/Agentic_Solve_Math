# Phase 2 TDD Implementation Plan

## Goal

Подготовить следующий этап работы так, чтобы detailed coding шёл через test-first implementation, а не через ad-hoc наращивание root runtime.

## Principle

Каждая новая возможность сначала получает:

1. явный contract;
2. тесты на happy path;
3. тесты на failure modes;
4. только после этого реализацию.

## Scope of the next coding phase

Следующая coding phase должна покрыть:

- root contracts;
- organization manifests;
- ACL and visibility enforcement;
- router;
- handoff builder;
- delegation runtime;
- result ingestion;
- root logs integration;
- Agents SDK adapter layer;
- baseline tool/MCP adapters;
- dry-run end-to-end flow.

## Proposed module layout

Следующий слой кода рекомендуется вводить так:

- `workspace_orchestrator/contracts.py`
- `workspace_orchestrator/organization.py`
- `workspace_orchestrator/acl.py`
- `workspace_orchestrator/visibility.py`
- `workspace_orchestrator/communications.py`
- `workspace_orchestrator/router.py`
- `workspace_orchestrator/handoff.py`
- `workspace_orchestrator/delegation.py`
- `workspace_orchestrator/root_logs.py`
- `workspace_orchestrator/runs.py`
- `workspace_orchestrator/openai_runtime.py`
- `workspace_orchestrator/tooling/`

Внутри `tooling/` позже:

- `kaggle_bridge.py`
- `papers_bridge.py`
- `mcp_policy.py`

## Iteration 1 - Contracts first

### Write tests first

Нужно сначала написать тесты для:

- сериализации `TaskRequest`;
- валидации `RoutingDecision`;
- валидации `HandoffPackage`;
- валидации `DelegationResult`;
- валидации `EscalationRequest`;
- валидации `RunTrace`.

### Then implement

Реализовать dataclass/pydantic layer для canonical runtime contracts.

### Done criterion

`pytest` подтверждает, что contracts:

- валидируются;
- сериализуются;
- reject malformed inputs.

## Iteration 1B - Organization manifests and ACL graph

### Write tests first

Нужно сначала покрыть:

- валидацию `DepartmentManifest`;
- валидацию `AgentManifest`;
- communication ACL graph;
- hidden/read/write path policies;
- rule mutation scopes.

### Then implement

Сделать manifest layer для:

- department hierarchy;
- role rank;
- file visibility;
- callable peers;
- shared service agents;
- mutable rule scopes.

### Done criterion

Runtime знает не только "что за task", но и "кто что может видеть, вызывать и менять".

## Iteration 2 - Router

### Write tests first

Тесты на:

- routing в existing subproject;
- routing в root-only path;
- case `new_subproject_required`;
- case `unsupported_task`;
- boundary around malformed intake data.

### Then implement

Вынести current heuristic routing в отдельный модуль и сделать его явным и тестируемым.

### Done criterion

Router возвращает deterministic `RoutingDecision` и не зависит от ad-hoc CLI branching.

## Iteration 3 - Handoff package generation

### Write tests first

Тесты на:

- сборку `HandoffPackage` из `TaskRequest` + `ResearchPlan` + routing context;
- materialization handoff package в root-owned run directory;
- запрет записи handoff artifacts в папку подпроекта.

### Then implement

Сделать builder и file materializer для handoff bundles.

### Done criterion

Каждый существенный root-to-subproject запуск имеет воспроизводимый handoff artifact.

## Iteration 4 - Delegation runtime

### Write tests first

Тесты на:

- успешный local delegation run;
- отсутствие `main.py` или локального runtime entrypoint;
- non-zero exit code;
- timeout;
- malformed result package;
- invalid target path.

### Then implement

Вынести subprocess/runtime logic из CLI в отдельный execution layer.

### Done criterion

Root умеет безопасно запускать локальный runtime и собирать structured execution result.

## Iteration 5 - Result ingestion and root logs

### Write tests first

Тесты на:

- ingestion `DelegationResult`;
- append-only updates in root logs;
- no writes into subproject-local docs;
- correct update of root registry and journal.

### Then implement

Сделать helpers для:

- `USER_PROMPTS_LOG.md`
- `RESEARCH_JOURNAL.md`
- `AGENT_INTERACTIONS_LOG.md`
- topic/index updates

### Done criterion

После каждого substantial run root оставляет корректный audit trail.

## Iteration 6 - Agents SDK adapter layer

### Write tests first

Нужны contract tests на:

- conversion of internal contracts into agent inputs;
- routing between root roles;
- tool-policy checks;
- trace metadata propagation.

### Then implement

Сделать минимальный adapter между нашими internal contracts и `OpenAI Agents SDK`.

### Done criterion

Root runtime может поднять baseline team topology without breaking existing CLI scaffold.

## Iteration 7 - Tooling adapters

### `papers-bridge`

#### Tests first

Покрыть:

- source normalization;
- classification by source type;
- confidence/evidence labelling;
- failure on malformed external metadata.

#### Then implement

Сначала lightweight adapter над public scholarly APIs.

### `kaggle-bridge`

#### Tests first

Покрыть:

- auth discovery;
- competition slug handling;
- download command construction;
- submit request packaging;
- safe dry-run behavior.

#### Then implement

Сначала contract adapter, потом full integration.

## Iteration 8 - End-to-end dry run

### Write tests first

Создать fixture-подпроект и проверить:

- intake parsing;
- routing;
- handoff generation;
- local run;
- result ingestion;
- root logging.

### Then implement

Дотянуть integration wiring до состояния reproducible dry run.

### Done criterion

Команда `main.py` может выполнить demonstrable root-to-local cycle без вмешательства во внутреннюю память подпроекта.

## Testing structure recommendation

Рекомендуется добавить:

- `tests/test_contracts.py`
- `tests/test_organization.py`
- `tests/test_acl.py`
- `tests/test_visibility.py`
- `tests/test_communications.py`
- `tests/test_router.py`
- `tests/test_handoff.py`
- `tests/test_delegation.py`
- `tests/test_root_logs.py`
- `tests/test_openai_runtime.py`
- `tests/test_kaggle_bridge.py`
- `tests/test_papers_bridge.py`
- `tests/integration/test_root_dry_run.py`

## Verification discipline

На каждой итерации нужно прогонять:

- targeted unit tests;
- related integration tests;
- existing smoke tests root scaffold;
- manual CLI sanity checks if surfaced commands changed.

## Explicit non-goal of the next coding phase

Следующая фаза не должна сразу пытаться:

- построить self-improving super-system целиком;
- оптимизировать все subproject internals;
- делать production-scale remote MCP mesh.

Сначала нужно сделать надёжный, тестируемый и traceable control plane.

## Exit criterion

Phase 2 считается завершённой, когда:

- все core contracts покрыты тестами;
- root runtime работает через explicit handoff/result cycle;
- root logs обновляются автоматически и корректно;
- baseline Agents SDK integration выполнена;
- dry-run e2e проходит стабильно.

## Progress marker (2026-03-17)

Implemented in code so far:

- organization manifests for root and subproject teams;
- communication ACL and path visibility checks;
- runtime contracts:
  - `TaskRequest`
  - `RoutingDecision`
  - `ResearchPlan`
  - `ChangeRequest`
  - `HandoffPackage`
  - `DelegationResult`
  - `RunTrace`
- root-owned handoff materialization in `.agent_workspace/runs/<run_id>/`;
- root CLI commands:
  - `build-handoff`
  - `show-run`
  - `record-result`

Implemented tests so far:

- `tests/test_contracts.py`
- `tests/test_handoff.py`
- `tests/test_delegation.py`
- `tests/test_cli_runtime.py`

Meaning of this progress marker:

- Iteration 3 is materially in place.
- Iteration 4 now has a working root-owned run artifact baseline.
- Iteration 5 is still only partially complete because root logs are not yet updated automatically from the run lifecycle.

Still pending on the critical path:

- execution adapter that actually launches the delegated local runtime from the handoff package;
- structured ingestion of non-zero exit codes, timeouts and malformed result bundles;
- automatic root log updates from run completion;
- OpenAI Agents SDK adapter above this control plane.

## Progress marker (2026-03-17, execution slice)

Additional implementation completed:

- `ExecutionRecord` contract;
- root execution registry with compatibility profiles;
- execution adapter that launches delegated local runtimes from prepared runs;
- automatic trace transitions for:
  - `running`
  - `dry_run`
  - `awaiting_result`
  - `execution_failed`
- automatic ingestion of protocol-produced `subproject_result.json` into canonical `delegation_result.json`;
- root CLI command:
  - `execute-run`

Additional tests completed:

- `tests/test_execution.py`
- `tests/integration/test_root_dry_run.py`

Meaning of this progress marker:

- Iteration 4 is now materially implemented, not only planned.
- Failure-path coverage now includes non-zero exit and timeout handling.
- A real root-to-subproject dry-run path exists in integration tests.

Still pending after this slice:

- automatic root log updates triggered directly from run completion events;
- malformed incoming result bundle handling beyond current basic contract parsing;
- OpenAI Agents SDK adapter and team activation layer above this execution substrate.

## Progress marker (2026-03-17, root log sync slice)

Additional implementation completed:

- automatic root log synchronization from execution events;
- automatic root log synchronization from result ingestion events;
- idempotent sync tracking via `log_sync_state.json`;
- root log summary generation for:
  - `RESEARCH_JOURNAL.md`
  - `AGENT_INTERACTIONS_LOG.md`

Additional tests completed:

- `tests/test_root_logs.py`
- integration assertions in `tests/integration/test_root_dry_run.py`

Meaning of this progress marker:

- Iteration 5 is now materially in place for run lifecycle summaries.
- Root control plane no longer depends only on manual journal updates for routine run tracing.

Still pending after this slice:

- malformed incoming result bundle hardening;
- richer root registry/topic updates from run completion;
- OpenAI Agents SDK adapter and multi-agent activation layer.

## Progress marker (2026-03-17, OpenAI runtime adapter slice)

Additional implementation completed:

- inspectable OpenAI runtime spec layer in `workspace_orchestrator/openai_runtime.py`;
- SDK availability detection with explicit degraded mode when `agents` is not installed;
- runtime metadata propagation from prepared run handoff packages;
- mapping from organization manifests to:
  - handoff targets
  - shared-service tool targets
- bounded SDK bundle materialization for a selected entry agent;
- root CLI commands:
  - `sdk-status`
  - `runtime-summary`

Additional tests completed:

- `tests/test_openai_runtime.py`
- `tests/integration/test_root_runtime_summary.py`

Meaning of this progress marker:

- Iteration 6 is now materially in place as a real adapter layer, not only as documentation.
- The system can inspect and validate OpenAI team topology without requiring immediate SDK installation.
- Root runtime design is now grounded in executable contracts that preserve hierarchy, ACL intent and run metadata.

Still pending after this slice:

- direct invocation of `Runner` or equivalent SDK execution primitives against live models;
- wiring runtime-spec activation into the main orchestration loop;
- bridging hosted tools and future MCP-backed services into the SDK layer;
- deeper cycle-aware activation for large department graphs beyond the current bounded bundle.

## Progress marker (2026-03-17, live launch slice)

Additional implementation completed:

- live root launch runtime in `workspace_orchestrator/live_runtime.py`;
- persistent SQLite-backed session bootstrap for root and subproject runs;
- generic root-managed subproject commander runtime driven from root-owned handoff packages;
- root operational function tools for:
  - workspace inspection
  - intake parsing
  - runtime inspection
  - handoff creation
  - subproject activation
- subproject operational function tools for:
  - handoff inspection
  - local file reading
  - structured result recording
- auto-launch behavior for `main.py` when OpenAI bootstrap settings are present;
- root bootstrap files:
  - `.env.example`
  - `requirements.txt`

Additional tests completed:

- `tests/test_live_runtime.py`
- `tests/integration/test_root_launch_cli.py`

Meaning of this progress marker:

- The workspace now has a real launchable root runtime path, not only an inspectable spec layer.
- A user can prepare `.env`, run `main.py` from the root and enter the live orchestration path.
- Root can now activate a generic subproject commander runtime without patching subproject internals.

Still pending after this slice:

- validation against a real installed `openai-agents` environment and live models;
- richer tool coverage for every department role beyond the current operational baseline;
- deeper production hardening for long-running loops, retries and failure recovery.

## Progress marker (2026-03-18, model policy and live launch hardening slice)

Additional implementation completed:

- per-agent model selection in `workspace_orchestrator/model_policy.py`;
- runtime spec exposure of `preferred_model` and `model_rationale`;
- `.gitignore` and root `.env` bootstrap hygiene for secrets and runtime artifacts;
- ACL-bounded live operational tools for root editorial and subproject historian roles;
- SQLite session fallback from workspace storage to temp-backed storage when the local filesystem rejects journal I/O;
- friendly live launch error shaping for:
  - quota exhaustion
  - API connectivity failure
- root `main.py` process exit-code propagation.

Additional tests completed:

- `tests/test_model_policy.py`
- expanded `tests/test_openai_runtime.py`
- expanded `tests/test_live_runtime.py`
- expanded `tests/integration/test_root_launch_cli.py`
- `tests/test_root_entrypoint.py`

Meaning of this progress marker:

- Iteration 7 hardens the launch path from “assembled” to “operationally understandable”.
- The root entrypoint now behaves correctly in shells and automation.
- Real API verification has progressed far enough to show that the next blocker is quota, not local code wiring.

Still pending after this slice:

- successful live response from the configured OpenAI account after quota/billing is available;
- optional suppression or redirection of residual SDK-side stderr logs during failed API calls;
- deeper department-specific tool specialization and long-running recovery loops.
