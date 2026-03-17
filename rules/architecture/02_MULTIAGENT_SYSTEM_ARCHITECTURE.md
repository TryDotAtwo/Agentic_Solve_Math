# Multiagent System Architecture

## Target shape

Система должна иметь два уровня:

1. root orchestrator layer;
2. autonomous local project layers.

## Root orchestrator layer

Components:

- intake manager;
- project registry;
- source collection coordinator;
- architecture steward;
- global memory manager;
- cross-project synthesis agent;
- launcher / runtime controller.

Responsibilities:

- read intake;
- choose or create subproject;
- spawn local teams;
- coordinate global tasks;
- maintain root memory;
- preserve reproducibility.

## Local project layer

Каждый подпроект имеет собственную internal system:

- local docs;
- local AGENTS contract;
- local task board;
- local agents;
- local codebase;
- local artifacts;
- local summaries.

## Shared services layer

Shared services are cross-cutting but must be exposed as tools, not as implicit shared state:

- filesystem access;
- git context;
- web/source retrieval;
- paper search;
- artifact registry;
- submission service;
- notification service.

## Memory model

### Root memory

Stores:

- prompts;
- global journal;
- archive of topics;
- architecture decisions;
- coordination records.

### Local memory

Stores:

- local hypotheses;
- local runs;
- local evaluation notes;
- local theory notes;
- local backlog.

## Control flow

1. Intake enters root.
2. Root produces global brief.
3. Root selects local owner project.
4. Root activates local team.
5. Local team executes and updates its own layer.
6. Local team returns verified summaries.
7. Root updates global memory and cross-project architecture.

## Design rule

Global state must not become a substitute for local project state.
