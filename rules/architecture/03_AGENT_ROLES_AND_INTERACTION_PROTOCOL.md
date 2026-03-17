# Agent Roles And Interaction Protocol

## Root roles

### Intake Analyst

- parses incoming task;
- extracts official links and constraints;
- drafts the first brief.

### Project Router

- chooses existing project or creates a new one;
- decides ownership boundaries.

### Architecture Steward

- maintains system design docs;
- prevents boundary erosion between projects.

### Global Memory Curator

- updates prompt log;
- updates research journal;
- updates topic archive.

### Cross-project Synthesizer

- merges verified conclusions from multiple projects;
- identifies reusable patterns.

## Local project roles

### Engineering Lead

- solver pipeline;
- experiments;
- tooling;
- performance and correctness.

### Math/Theory Lead

- invariants;
- abstractions;
- proof routes;
- theory-backed heuristics.

### Literature Analyst

- papers;
- repos;
- notebooks;
- benchmark baselines.

### Evaluation And Submission Lead

- contract validation;
- scoring;
- autosubmit;
- leaderboard hygiene.

### Synthesis Reporter

- local summary docs;
- distilled decisions;
- handoff to root.

## Interaction artifacts

- task brief;
- source pack;
- experiment report;
- theory note;
- decision record;
- escalation note;
- submission record.

## Escalation conditions

Escalate to root if:

- a new subproject is needed;
- a global rule must change;
- multiple local projects conflict;
- official contract is ambiguous;
- a global architectural decision is required.
