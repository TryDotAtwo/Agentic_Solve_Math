## CayleyPy-444-Cube – Kaggle subproject

This subproject is dedicated to the **CayleyPy-444-Cube** Kaggle competition (assumed URL: `https://www.kaggle.com/competitions/cayleypy-444-cube`).  
If the actual competition URL or slug differs, it should be updated here and in the autosubmit configuration.  
Everything in this folder is intended to be self-contained and independent from other projects in the workspace.

### Goal and evaluation metric

- **High-level goal (assumption / TODO)**:  
  Participants are given scrambled states of a \(4 \times 4 \times 4\) Rubik’s cube (a "4×4×4 cube") and must produce sequences of moves that solve each cube.  
  The task is expected to be closely related to finding short or near‑optimal solutions in the Cayley graph of the 4×4×4 cube group.

- **Evaluation metric (assumption / TODO)**:  
  The public score is probably based on the *total number of moves* (or an equivalent cost) needed to solve all cubes in the submission file, i.e. fewer total moves ⇒ better score.  
  This mirrors the design of the CayleyPy Pancake Problem competition, where the objective is to minimize the total cost of solutions.

These assumptions must be checked against the official competition description once the Kaggle page is available locally or via browser.

### First engineering milestone

The **first engineering milestone** for this subproject is purely infrastructural:

1. **Understand the submission format**
   - Clarify required columns and types in the submission CSV (ids, cube representation / permutation, move sequence, etc.).
   - Document how cube states and moves are encoded (strings, comma-separated tokens, face notation, etc.).
2. **Set up autosubmit**
   - Create a small, reusable Python module that:
     - loads and validates a submission CSV;
     - checks that required columns exist and have the right types;
     - calls Kaggle CLI (`kaggle competitions submit ...`) when available;
     - falls back to HTTP API submission if CLI is broken, following the Pancake project’s `main.py` pattern;
     - logs attempts and responses for reproducibility.
3. **Verify a test submission**
   - Prepare a dummy or baseline submission with the correct schema.
   - Run the local validation checks.
   - Perform a real Kaggle submission (once credentials are configured) and verify that:
     - the file is accepted by Kaggle;
     - the score is reported as expected (even if it is a trivial baseline).

For details, see the local `docs/` folder:

- `docs/01_COMPETITION_OVERVIEW.md` – problem brief, data and submission format.  
- `docs/02_AUTOSUBMIT_SETUP.md` – autosubmit design, module layout, and usage instructions.  
- `docs/03_STATE_AND_GROUP_STRUCTURE.md` – conceptual description of the 4×4×4 state space and underlying group / Cayley graph (with explicit assumptions).  
- `docs/04_POTENTIAL_HYPOTHESES.md` – candidate mathematical and algorithmic hypotheses for future analysis.

Additionally, there is a minimal baseline script:

- `generate_dummy_submission.py` – loads `test.csv` from this directory, builds a trivially valid `submission.csv` with:
  - `id` copied from the test file;
  - `solution` as an empty string for every row;
  then runs the same schema validation as the autosubmit module. This script is intended purely to check the end‑to‑end pipeline (load test → generate submission → validate → autosubmit), not to provide a meaningful solver.

### Search-based solver (state-aware)

The subproject contains a state-aware beam search that actually solves cubes:

- `cube_engine.py` – applies generators from `puzzle_info.json` to state vectors; `parse_state`, `apply_move`, `apply_path`, `is_solved`.
- `search/` package
  - `moves.py` – move alphabet from `data/puzzle_info.json`; `.`-separated `path` encoding.
  - `solver_beam.py` – two-stage beam search over real states (fast pass + hard-instance retry).
  - `solver_random_beam.py` – legacy skeleton (abstract, no state simulation) with:
    - configurable `SearchConfig` (max depth, beam width, branching, random seed);
    - a pluggable heuristic function over `(state_repr, moves_so_far)`;
    - `solve_instance` / `solve_batch` interfaces returning move sequences or ready-to-submit solution strings.
  - `__init__.py` – high-level description and aggregation.
- `solve_with_search.py` – example script that:
  - assumes `test.csv` has columns `id` and `state` (ASSUMPTION);
  - runs `solve_batch` on the `state` column;
  - writes `submission_search.csv` with `id` and `solution`.

At this stage, the search solver operates on abstract state strings and does not yet simulate the true 4×4×4 cube dynamics. It is designed to be upgraded once a concrete cube engine and stronger heuristics (including pattern-database or learned value functions) are available.

### NN + search hybrid scaffolding

To prepare for neural-network–guided search, the subproject includes:

- `nn/` package
  - `__init__.py` – high-level description of the role of NN components and their separation from search.
  - `schema.py` – defines:
    - `StateTensorSpec` and `TargetSpec` for describing NN inputs/targets;
    - `default_state_tensor_spec()` / `default_target_spec()` as placeholders to be refined once a concrete encoding and move set are chosen.
  - `interfaces.py` – defines:
    - `PolicyValueModel` protocol (a minimal interface any policy+value NN must implement);
    - `NNGuidedHeuristic`, an adapter that turns a `PolicyValueModel` into a heuristic function usable by `search.solver_random_beam`;
    - `num_moves()` helper returning the size of the move alphabet.

Design principles:

- This repository only contains the *interfaces* and *adapters*; heavy ML frameworks and training code should live in a dedicated ML project.
- At inference time, a trained model that implements `PolicyValueModel` can be injected into `NNGuidedHeuristic` and used as the `heuristic` argument in `solve_instance` / `solve_batch`.

### Experiment runners

- `run_experiment.py`
  - CLI entry for local experiments:
    - `--mode dummy` – generate `submission_dummy.csv` via the trivial baseline (empty solutions).
    - `--mode search` – generate `submission_search.csv` via the search-based scaffold.
  - Designed to be extended with additional modes as stronger solvers are implemented.
- `run_best.py`
  - Thin wrapper that currently runs the search-based solver to produce `submission_best.csv`.
  - Intended to always point to the strongest validated configuration at a given time.

See also `docs/06_EXPERIMENT_WORKFLOW.md` for narrative guidelines on how to use these runners together with `submission/autosubmit.py` and how to log experiments in line with the root standards.

### Math track integration

The math-side of this subproject is organized around:

- `docs/03_STATE_AND_GROUP_STRUCTURE.md` – group / state-space viewpoint on the 4×4×4 cube.
- `docs/04_POTENTIAL_HYPOTHESES.md` – numbered hypotheses about metrics, invariants, hardness, and cross-problem analogies.
- `docs/07_MATH_TRACK_INTEGRATION.md` – how local hypotheses and experiments in this subproject should be linked to the global math-hypothesis lab and root research journals.

Engineering experiments that touch these hypotheses (e.g. new heuristics inspired by `H4C_metric_*` or difficulty analyses tied to `H4C_hard_*`) should reference the relevant IDs and, when appropriate, promote mature hypotheses to the global math-hypothesis project for deeper analysis.

### Leaderboard-oriented strategy

For leaderboard-focused work, see:

- `docs/08_LEADERBOARD_STRATEGY.md` – high-level plan for:
  - building a baseline ladder (infrastructure → search-only → search+heuristics → NN-guided search);
  - organizing multi-stage solving pipelines (fast pass + targeted improvement on hard instances);
  - managing solver configurations and submission experiments under Kaggle limits;
  - using `run_best.py` as the canonical entry point for the current strongest configuration.



### Math track

This subproject has a dedicated **math track** focused on:

- describing the **state space** and **group/Cayley-graph structure** of the 4×4×4 cube (`docs/03_STATE_AND_GROUP_STRUCTURE.md`);
- collecting **hypotheses and conjectures** about metrics, invariants, and decompositions that might guide solvers (`docs/04_POTENTIAL_HYPOTHESES.md`).

The intention is that, once the competition spec and baselines are stable, this math track will interface with the broader **math‑hypothesis lab** in the workspace, so that structural insights and experimental evidence can be shared across CayleyPy problems.

