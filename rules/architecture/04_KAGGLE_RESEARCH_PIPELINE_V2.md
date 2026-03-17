# Kaggle Research Pipeline V2

## Principle

Root owns orchestration. Local subproject owns execution.

## Step 1. Intake

- root reads `kaggle_intake/*.md`;
- logs prompt;
- starts journal entry.

## Step 2. Official contract capture

- obtain rules;
- obtain official files;
- confirm submission shape;
- mark unknowns.

## Step 3. Global brief

- competition objective;
- metric;
- file contract;
- constraints;
- candidate baseline directions;
- risk register.

## Step 4. Ownership decision

- choose existing subproject or create new one;
- define local team;
- define root-facing outputs.

## Step 5. Local source pack

Inside local project:

- analyze discussions, repos, notebooks, papers;
- split engineering and theory strands;
- create local research backlog.

## Step 6. Local implementation loop

- hypothesis;
- experiment or analysis;
- correctness check;
- metric evaluation;
- artifact storage;
- local summary update.

## Step 7. Submission loop

- validate contract;
- generate submission;
- dry-run checks;
- submit;
- capture submission metadata;
- summarize result.

## Step 8. Root synthesis

- update `RESEARCH_JOURNAL.md`;
- update `rules/memory/KAGGLE_TOPICS_ARCHIVE.md`;
- update architecture docs if reusable pattern discovered.

## Exit criteria for stage 1

The system is acceptable when it can reproducibly do all of the following:

- ingest a Kaggle task;
- spin up or assign a local project;
- search and classify sources;
- run local research loops;
- validate and submit to Kaggle;
- preserve evidence for later paper writing.
