# MCP Server Strategy

## Goal

Определить реалистичный tool/MCP stack для первого этапа root-level multi-agent system, который:

- помогает исследовать Kaggle competitions;
- поддерживает поиск и чтение научных источников;
- не ломает автономию подпроектов;
- остаётся воспроизводимым и проверяемым;
- не заставляет нас переусложнять v1.

## Key design principle

На первом этапе нужно думать не только про MCP servers, но про весь **tooling stack**:

1. что уже даёт OpenAI platform;
2. что стоит подключить как local/shared MCP;
3. что лучше реализовать как custom domain bridge;
4. что следует отложить до появления реальной потребности.

## Official guidance that matters

По [Using tools](https://platform.openai.com/docs/guides/tools) OpenAI already supports:

- web search;
- function tools;
- remote MCP;
- other hosted tool patterns.

По [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp):

- approvals for remote MCP are important by default;
- data shared with remote MCP servers should be reviewed and preferably logged;
- подключать лучше trusted/official servers, а не случайные third-party proxies.

Это означает, что на v1 нам не нужно превращать всё в MCP. Часть задач уже лучше решается hosted tools + local adapters.

## Recommended layered stack

### Layer 0 - OpenAI hosted tools first

Использовать в первую очередь то, что уже даёт OpenAI runtime:

- web search для online research;
- function tools для локальных Python adapters;
- remote MCP только там, где он реально полезнее локального bridge.

Почему это важно:

- меньше инфраструктуры на старте;
- проще трассировать;
- меньше surface area для доверия и секрета;
- быстрее выйти к рабочему root runtime.

## Layer 1 - Shared local MCP baseline

Как общий нейтральный слой для root/local systems подходят:

- filesystem-oriented access;
- git-oriented access;
- выборочные local utility servers, когда это реально даёт стандартизованный интерфейс.

Официальный reference catalog:

- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

Минимальный baseline для v1:

- filesystem-like access;
- git/repository access.

Это уже достаточно для:

- чтения project state;
- построения reproducible agent workflows;
- безопасной работы с локальными артефактами.

## Layer 2 - Custom domain bridges

### `kaggle-bridge`

Это приоритетный custom bridge.

Он должен закрывать:

- competition metadata retrieval;
- download orchestration;
- local path normalization;
- submission packaging;
- submit logging;
- safe dry-run / approval policy.

Строить поверх официального Kaggle API/CLI:

- [Official Kaggle API repository](https://github.com/Kaggle/kaggle-api)

Важно: в root должен жить только bridge/contract layer. Competition-specific submit logic и validators должны оставаться в подпроектах.

### `papers-bridge`

Это второй приоритетный custom bridge.

Он должен закрывать:

- paper lookup;
- metadata normalization;
- source classification;
- citation-oriented export;
- evidence labelling.

Primary APIs:

- [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)
- [Semantic Scholar API](https://api.semanticscholar.org/api-docs/)
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

## Layer 3 - Optional remote/shared integrations

Подключать позже и только при явной пользе:

- GitHub MCP, если root/subprojects начнут реально опираться на GitHub workflows;
- Playwright/browser-style tooling, если окажется, что hosted web search и local fetch-adapters недостаточны для Kaggle UI flows;
- дополнительные remote MCP integrations только под конкретную verified workflow need.

## Trust and approval policy

### Require approval by default

- подключение нового remote MCP server;
- отключение approval mode для remote MCP calls;
- действия, которые могут утянуть sensitive data наружу;
- использование third-party hosted MCP without clear trust story.

### Always log

- какой server подключён;
- какие данные туда уходят;
- почему это подключение было нужно;
- где зафиксировано решение о доверии.

Это соответствует рекомендациям из [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp).

## Recommended v1 stack

Если выбирать строго practical v1, то я рекомендую такой стартовый набор:

1. OpenAI hosted web/tool layer
2. Local filesystem/repository access
3. `papers-bridge`
4. `kaggle-bridge`

При этом:

- remote MCP by default не является обязательным компонентом v1;
- GitHub/Playwright integrations лучше держать отложенными;
- root должен оставаться небольшим control plane, а не giant integration hub.

## What should not happen

- Не нужно сразу собирать большой zoo из MCP servers.
- Не нужно переносить в root все competition-specific adapters подпроектов.
- Не нужно доверять random third-party remote MCP endpoints без logging/approval policy.

## Conclusion

На первом этапе лучшая стратегия не "максимум MCP", а:

- минимум инфраструктуры;
- максимум controllability;
- hosted tools where possible;
- custom bridges where domain-specific access really matters;
- strict approval/logging for remote MCP.
