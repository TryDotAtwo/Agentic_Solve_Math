## Leaderboard-oriented strategy for CayleyPy-444-Cube

> **Status:** high-level strategy document; concrete numbers will depend on real Kaggle feedback.

### 1. Baseline ladder

1. **Infrastructure baseline**
   - `generate_dummy_submission.py` + `submission/autosubmit.py`.
   - Purpose: verify the pipeline, not to score well.
2. **Search-only baseline**
   - `solve_with_search.py` using the current search scaffold.
   - Measure:
     - typical solution lengths;
     - runtime per cube and for full `test.csv`;
     - first real Kaggle scores.
3. **Search + better heuristics**
   - Integrate features inspired by `H4C_metric_*` and `H4C_invariant_*` into the heuristic function:
     - phase-oriented penalties;
     - simple parity / anomaly detectors;
     - (later) small pattern-database style components.

Each rung of the ladder should have:

- a named configuration;
- a reference submission file;
- a recorded Kaggle score.

### 2. Multi-stage solving pipeline

To balance quality and runtime:

- **Stage 1: fast pass**
  - Use a fast, shallow solver configuration (e.g. small beam width, low depth).
  - Aim to produce solutions for all cubes within a tight time budget.
- **Stage 2: targeted improvement**
  - Identify \"hard\" cubes based on:
    - search metrics (e.g. heuristic values, branching statistics);
    - features related to `H4C_hard_*` (parity, edge pairing difficulty).
  - Re-run only these cubes with:
    - deeper search;
    - stronger heuristics or NN-guided search when available.

The final submission can combine:

- Stage-1 solutions for easy instances;
- Stage-2 solutions for hard instances.

### 3. Ensembles and configuration selection

As more solvers appear:

- Maintain a small set of **candidate configurations**:
  - different search parameters;
  - different heuristic / NN versions.
- For each configuration:
  - run `run_experiment.py` to generate a submission-like file;
  - (optionally) submit to Kaggle, being mindful of daily submission limits;
  - record:
    - configuration ID;
    - Kaggle score;
    - runtime characteristics.

Ensembling options:

- For each cube instance, select the best solution among several solvers using:
  - internal score estimates (e.g. move count, heuristic value);
  - or external validation (if a cheap local evaluator becomes available).

### 4. Practical leaderboard tactics

- Use early days of the competition to:
  - explore the space of configurations broadly;
  - map out the Pareto front \"score vs runtime\".
- Once a strong configuration is identified:
  - treat `run_best.py` as the canonical way to produce leaderboard submissions;
  - only change it when a new configuration is clearly superior and well-documented.

All substantial leaderboard-relevant changes (new best scores, shifts in strategy) should be:

- documented in this subproject’s docs;
- summarized in the root `RESEARCH_JOURNAL.md` with links back to the relevant files and configurations.

