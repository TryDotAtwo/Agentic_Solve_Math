# Access Control and Visibility Model

## Goal

Сделать так, чтобы ограничения ролей задавались:

- не только текстовыми правилами;
- но и жёстким кодовым enforcement;
- с ограничением видимости файлов, правил, инструментов и каналов связи.

## Non-negotiable principle

Если агенту что-то "нельзя", это должно означать не только "нельзя по инструкции", но и:

- путь не виден;
- файл не индексируется;
- tool не доступен;
- peer agent не вызывается;
- write attempt блокируется runtime.

## What must be controlled

### 1. File visibility

Для каждого агента должна быть своя видимая область:

- readable roots;
- writable roots;
- hidden roots;
- rules roots;
- artifact roots.

### 2. Communication graph

Для каждого агента должен быть явный allowlist:

- какие peer agents доступны;
- какие departments доступны;
- какие heads доступны;
- какие shared service agents доступны.

### 3. Tool permissions

Для каждого агента нужен allowlist tools:

- web research;
- file search;
- repo search;
- experiment launch;
- submission ops;
- rule editing;
- MCP connectors.

### 4. Rule mutation authority

Нужно отдельно зафиксировать:

- кто может менять hard rules;
- кто может менять local department rules;
- кто может только создавать change requests.

## Access levels

### Level A - Root executive

- `Root Orchestrator`
- максимальный обзор root layer;
- неограниченный доступ к root org docs;
- неограниченный доступ к root run artifacts;
- no direct ownership of subproject local memory.

### Level B - Department heads

- видят свой департамент полностью;
- видят shared coordination docs;
- могут общаться с другими heads;
- могут изменять department-local overlays;
- не получают полный обзор чужих department internals автоматически.

### Level C - Department staff

- видят только свой департамент;
- видят явно разрешённые shared service agents;
- видят task package, а не всю оргструктуру;
- не могут менять policy files без head approval.

### Level D - Shared service agents

- видят только минимально нужный input;
- не получают широкий доступ к проекту;
- работают как bounded callable specialists.

### Level E - External tool adapters

- не получают прямой доступ к лишнему контексту;
- получают только sanitized request payload.

## Required runtime objects

Для кодовой реализации понадобятся как минимум:

- `DepartmentManifest`
- `AgentManifest`
- `VisibilityPolicy`
- `ToolPolicy`
- `CommunicationACL`
- `RuleLayer`
- `ChangeRequest`
- `ApprovalRecord`
- `AccessViolation`

## Required fields in `AgentManifest`

- `agent_id`
- `role`
- `department`
- `rank`
- `read_roots`
- `write_roots`
- `hidden_roots`
- `callable_agents`
- `callable_departments`
- `shared_service_agents`
- `allowed_tools`
- `mutable_rule_scopes`
- `escalation_targets`
- `result_schema`

## Enforcement points

### Filesystem gateway

Все file operations должны идти не напрямую в ОС, а через visibility-aware layer.

Он обязан:

- фильтровать directory listing;
- фильтровать search results;
- запрещать чтение hidden paths;
- запрещать запись вне `write_roots`.

### Search gateway

`rg`-подобный поиск и индексатор должны видеть только разрешённые roots, иначе сотрудник сможет "случайно" узнать о скрытых файлах.

### Agent dispatcher

Вызов одного агента другим должен проходить через ACL-aware dispatcher.

Если peer не разрешён:

- вызов блокируется;
- создаётся audit event;
- при необходимости создаётся `EscalationRequest`.

### Tool dispatcher

Tool calls должны проверяться на уровне runtime, а не только prompt instructions.

### Write gateway

Каждая запись должна проверять:

- path scope;
- rule scope;
- need for approval;
- whether this write belongs to agent rank.

## Hidden by design examples

### Root staff agent

Сотрудник editorial department не должен автоматически видеть:

- все MCP policies;
- все tool credentials;
- внутренние drafts других departments;
- внутренности подпроектов.

### Subproject staff agent

Сотрудник подпроекта не должен автоматически видеть:

- root org design files;
- root department internals;
- соседние подпроекты;
- root-wide secret-bearing integrations.

### Shared search agent

Даже shared search agent не должен видеть полный workspace; он должен получать узкий request payload и возвращать structured findings.

## Rule layering model

### Layer 1 - Immutable root rules

Глобальные ограничения root layer.

### Layer 2 - Root department overlays

Меняются root department head внутри допустимого контура.

### Layer 3 - Subproject immutable export rules

То, что root задаёт подпроекту и что локальная команда не может отменить.

### Layer 4 - Subproject department overlays

Локальные департаментные правила подпроекта.

## Suggested implementation path

### Step 1

Сделать manifests и ACL contracts.

### Step 2

Сделать visibility-aware file and search gateways.

### Step 3

Сделать communication dispatcher с ACL.

### Step 4

Сделать write gateway и approval flow.

### Step 5

Привязать всё это к Agents SDK runtime adapters.

## Required tests

Нужны отдельные тесты на:

- hidden paths are not listed;
- forbidden files are not searchable;
- forbidden peer calls are rejected;
- staff cannot mutate department rules without approval;
- subproject agent cannot write root files;
- root staff cannot read hidden subproject local memory;
- shared service agents receive only narrowed payloads.

## Main conclusion

Для нашей системы ACL и visibility model не являются "дополнительной безопасностью". Это базовая часть архитектуры, без которой hierarchical multi-agent organization не будет настоящей, а останется только красивым описанием ролей.
