# Agent Protocols

## Цель

Зафиксировать интерфейсы между root orchestrator и изолированными подпроектами.

## Protocol 1 - Intake To Root

### Input

- markdown-файл в `kaggle_intake/`
- пользовательские уточнения в чате

### Output

- parsed links;
- initial problem brief;
- routing decision;
- запись в root logs.

## Protocol 2 - Root To Subproject Handoff

### Root sends

- task id or topic slug;
- concise goal;
- confirmed and unconfirmed facts;
- source list;
- expected deliverables;
- escalation rules.

### Subproject returns

- local plan;
- major findings;
- canonical local docs;
- blockers;
- requests back to root.

## Protocol 3 - Research Source Collection

Каждый исследовательский агент обязан разделять источники на типы:

- official competition materials;
- docs and rules;
- papers;
- notebooks;
- repositories;
- discussions;
- inferred ideas.

Выводы должны маркироваться как:

- `confirmed`
- `partially confirmed`
- `needs verification`
- `hypothesis`

## Protocol 4 - Submission Safety

Перед отправкой на Kaggle подпроектная команда обязана подтвердить:

1. correct competition slug;
2. correct submission columns;
3. row count and row ordering;
4. отсутствие пустых или malformed paths;
5. local validator success;
6. наличие журнала того, что именно было отправлено.

Root получает вверх только итог:

- что отправлено;
- куда;
- с каким summary;
- где лежит canonical local report.

## Protocol 5 - Documentation Synchronization

### Root updates

- root logs;
- topic registry;
- architecture docs;
- cross-project summary.

### Subproject updates

- local README/docs;
- local experiment logs;
- local result tables;
- local hypotheses and analysis.

## Protocol 6 - Escalation

Эскалировать в root нужно, если:

- нужен новый подпроект;
- нужен cross-project synthesis;
- локальное решение меняет глобальную архитектуру;
- нужен доступ к внешним инструментам;
- конфликтуют локальные и root-level требования.

## Protocol 7 - Hierarchical Communication

### Root level

- `Root Orchestrator` общается только с heads департаментов.
- Heads департаментов общаются:
  - с `Root Orchestrator`;
  - с heads других департаментов;
  - со своими staff agents;
  - с явно разрешёнными shared service agents.
- Staff agents общаются:
  - со своим head;
  - с staff внутри своего департамента;
  - с явно разрешёнными shared service agents.

### Subproject level

- `Subproject Commander` общается только с heads локальных департаментов и с root boundary.
- Heads локальных департаментов общаются:
  - с `Subproject Commander`;
  - с heads других локальных департаментов;
  - со своими staff agents;
  - с разрешёнными shared service agents.
- Staff локальных департаментов не должны напрямую общаться с root roles.

### Shared service exception

Некоторые агенты могут быть объявлены shared service agents и вызываться напрямую несколькими ролями:

- search agents;
- history agents;
- отдельные audit/tooling utility agents.

Но и эти вызовы должны проходить через explicit ACL.

## Protocol 8 - Rule Mutation

### Immutable rules

- Root hard rules меняются только root executive flow.
- Подпроект не может менять root hard rules.

### Department-local overlays

- Head департамента может менять правила своих сотрудников только внутри своего namespace.
- Такое изменение не должно расширять права за пределы root-defined envelope.

### Change requests

Если департамент или подпроект хочет изменить:

- глобальные правила;
- число департаментов;
- число сотрудников;
- graph communication;
- tool permissions;

это оформляется как explicit change request вверх по иерархии.

## Protocol 9 - Root-Owned Handoff Runs

Every root-to-subproject delegation cycle must be materialized in a root-owned run directory:

- `.agent_workspace/runs/<run_id>/handoff.json`
- `.agent_workspace/runs/<run_id>/task_request.json`
- `.agent_workspace/runs/<run_id>/routing_decision.json`
- `.agent_workspace/runs/<run_id>/research_plan.json`
- `.agent_workspace/runs/<run_id>/trace.json`

When a delegated team reports back, the result is recorded only through:

- `.agent_workspace/runs/<run_id>/delegation_result.json`

Rules for this lifecycle:

- root owns the run directory and may update `trace.json`;
- subprojects are referenced through `canonical_paths`, not mirrored into root memory;
- `trace.json` is the canonical status register for the run;
- handoff preparation and result recording must stay reproducible through CLI/runtime helpers;
- the default root-side requester for research handoffs is the responsible department head, not arbitrary staff.

Current root CLI surface:

- `build-handoff`
- `show-run`
- `record-result`

## Protocol 10 - Root Execution Adapter

Prepared runs may be activated by the root execution adapter.

Current execution rules:

- root resolves the target subproject from the handoff package;
- root chooses an execution profile for the target project;
- root launches only the project-local `main.py`;
- stdout/stderr and execution metadata are written into the root-owned run directory;
- `trace.json` is updated for:
  - `running`
  - `dry_run`
  - `awaiting_result`
  - `execution_failed`
  - final result status after result ingestion

Current execution artifacts:

- `.agent_workspace/runs/<run_id>/execution_record.json`
- `.agent_workspace/runs/<run_id>/execution_stdout.txt`
- `.agent_workspace/runs/<run_id>/execution_stderr.txt`

Protocol-aware subprojects may additionally write:

- `.agent_workspace/runs/<run_id>/subproject_result.json`

If `subproject_result.json` exists and matches the handoff contract, root ingests it into the canonical:

- `.agent_workspace/runs/<run_id>/delegation_result.json`

Current root CLI surface for execution:

- `execute-run`

Important boundary:

- root may launch a subproject runtime;
- root still does not edit subproject internals directly;
- legacy subprojects may be launched in a safety-biased compatibility mode until they become handoff-aware.

## Protocol 11 - Automatic Root Log Sync

Run lifecycle events must not live only inside `.agent_workspace`.

Current policy:

- execution events sync into root logs automatically;
- result events sync into root logs automatically;
- synchronization is idempotent per run/event key;
- root logs remain summaries, while `.agent_workspace/runs/<run_id>/` remains the canonical artifact store.

Current synchronized root logs:

- `rules/logs/RESEARCH_JOURNAL.md`
- `rules/logs/AGENT_INTERACTIONS_LOG.md`

Current run-local sync state:

- `.agent_workspace/runs/<run_id>/log_sync_state.json`

## Protocol 12 - OpenAI Runtime Spec And Lazy SDK Activation

The OpenAI runtime layer must remain inspectable even when the local Python environment does not yet have the `agents` package installed.

Current policy:

- the canonical source of runtime topology is an inspectable team spec, not an opaque live object graph;
- runtime specs are derived from organization manifests plus optional run-scoped handoff metadata;
- shared service agents map to direct tool-style targets;
- non-shared callable agents map to handoff targets;
- SDK activation happens through a lazy import boundary so the rest of the control plane stays testable without the package.

Current root CLI surface for runtime inspection:

- `sdk-status`
- `runtime-summary`

Current implementation boundary:

- runtime specs may be built for both root and subproject teams;
- contextual metadata may be injected from a prepared run id;
- a bounded SDK bundle may be materialized from the spec for a selected entry agent;
- absence of the SDK is reported explicitly instead of breaking unrelated orchestration features.
