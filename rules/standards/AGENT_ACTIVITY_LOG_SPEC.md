# Agent Activity Log Spec

## Purpose

Спецификация для подробного логирования значимых действий root orchestrator и локальных команд.

## Two-level rule

Логирование должно быть двухуровневым:

1. local project logs inside the owning subproject;
2. global narrative summary in root-managed memory.

## Root-level mandatory records

- user prompt trace in `rules/logs/USER_PROMPTS_LOG.md`;
- session summary in `rules/logs/RESEARCH_JOURNAL.md`;
- multi-agent coordination in `rules/logs/AGENT_INTERACTIONS_LOG.md` when relevant.

## Minimal activity fields

- timestamp;
- actor or agent role;
- scope (`root` or subproject path);
- action;
- inputs;
- outputs;
- decisions;
- risks / unknowns;
- next step.

## Rule

Если действие локальное и не меняет global layer, оно должно логироваться локально и только потом при необходимости конденсироваться в root summary.
