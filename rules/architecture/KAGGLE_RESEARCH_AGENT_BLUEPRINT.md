# Kaggle Research Agent Blueprint

## Target For Stage 1

Построить root-level мультиагента, который умеет:

- принимать новую Kaggle-задачу через `kaggle_intake/`;
- разбирать markdown и выделять official links, notebooks, papers, repos и приоритеты;
- определять, нужен новый подпроект или подходит существующий;
- готовить handoff package;
- запускать локальный entrypoint подпроекта;
- сохранять root-level traceability;
- поддерживать путь до безопасного submission.

## Capability Set

### Intake

- parse markdown;
- classify links;
- extract constraints;
- identify competition slug.

### Research

- искать official docs;
- искать papers, repos, notebooks и discussions;
- выделять baseline ideas;
- собирать curated source map.

### Orchestration

- назначать subagents;
- формировать plan;
- выбирать subproject team;
- собирать return summaries.

### Kaggle Ops

- проверять dataset/download contract;
- валидировать submission format;
- запускать autosubmit path;
- сохранять trace of submission attempts.

## Reference Patterns To Reuse From `CayleyPy_Pancake/`

- хорошие entry points и runners;
- дисциплина логирования результатов;
- оформленные docs для агентов;
- качественный feedback loop для пользователя;
- GPU beam search как пример вычислительно сильного инженерного трека;
- явное разделение solve / evaluate / compare / submit.

## What To Improve Beyond Pancake

- убрать жёсткую предметную привязку к одной задаче;
- отделить root orchestration от local solver implementation;
- формализовать handoff между root и подпроектами;
- добавить paper-grade traceability и source graph;
- систематизировать internet research и article discovery;
- ввести строгий root/subproject boundary.

## First Deliverables

1. Root launcher.
2. Workspace discovery.
3. Intake parser.
4. Root documentation restructure.
5. Architecture docs for future coding.
6. Subproject delegation hooks.
