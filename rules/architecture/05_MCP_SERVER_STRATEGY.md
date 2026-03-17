# MCP Server Strategy

## Decision principle

Для этого проекта лучше использовать гибридную схему:

- **official or well-maintained MCP servers** для общих capabilities;
- **custom domain MCP servers** для Kaggle, papers и project artifacts.

Это лучше, чем строить critical workflow на случайных community servers без понятной ответственности и воспроизводимости.

## Recommended core MCP servers

### 1. Filesystem MCP

Use for:

- controlled project file access;
- artifact inspection;
- local document reading.

Reason:

- базовая capability почти для всех агентов;
- есть официальный reference implementation в official MCP servers repository.

### 2. Git MCP

Use for:

- repo state inspection;
- branch diff context;
- commit-level traceability.

### 3. Fetch / HTTP MCP

Use for:

- retrieving official competition pages;
- collecting docs and source material;
- pulling machine-readable resources.

### 4. Memory MCP

Use for:

- explicit long-lived structured memory;
- agent handoff state;
- cross-session context packaging.

### 5. GitHub MCP

Use for:

- inspecting external repos;
- comparing baselines;
- issue / PR / code navigation where relevant.

### 6. Browser Automation MCP

Recommended use:

- browser-driven verification steps;
- competition page inspection;
- flows that CLI cannot cover.

## Domain-specific MCP servers to build ourselves

### A. `kaggle-mcp`

Should wrap the **official Kaggle CLI** / Kaggle API and expose:

- competition metadata fetch;
- file listing and download;
- submission validation;
- submission upload;
- submission status/history.

Why build it ourselves:

- Kaggle integration is mission-critical;
- we need traceable logs, reproducible parameters, and project-aware ownership;
- custom server can enforce local-subproject isolation and artifact logging.

### B. `papers-mcp`

Should expose:

- search across scientific sources;
- paper metadata fetch;
- citation capture;
- export into structured local notes.

Preferred upstreams:

- Semantic Scholar API;
- Crossref REST API;
- arXiv where appropriate.

### C. `artifact-registry-mcp`

Should expose:

- experiment registry;
- artifact lookup;
- run metadata;
- canonical-summary pointers.

Likely backend:

- SQLite plus filesystem paths.

## Servers to avoid as primary dependencies

- opaque third-party Kaggle MCP servers with unclear maintenance;
- any server that directly mutates multiple projects without ownership boundaries;
- any server that hides provenance of fetched data.

## Security and reproducibility rules

- credentials must stay outside docs and logs;
- every server action that changes competition state must be logged;
- submission actions must record: file, project, competition slug, message, timestamp;
- source retrieval must keep URL provenance.

## Current external references

- Official MCP servers repository: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- Official MCP documentation: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Official Kaggle API repository: [github.com/Kaggle/kaggle-api](https://github.com/Kaggle/kaggle-api)
- Semantic Scholar API docs: [api.semanticscholar.org](https://api.semanticscholar.org/api-docs/graph)
- Crossref REST API docs: [crossref.org/documentation/retrieve-metadata/rest-api](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

## Recommendation summary

Start with:

- filesystem;
- git;
- fetch;
- memory;
- github;
- browser automation;
- custom `kaggle-mcp`;
- custom `papers-mcp`;
- custom `artifact-registry-mcp`.

