## Engineering summary – CayleyPy-444-Cube

> **Status:** living canonical summary of engineering progress for this subproject.

### 1. Current infrastructure status

- Submission interface:
  - `docs/01_COMPETITION_OVERVIEW.md` defines the hard contract for `submission.csv`:
    - columns: `id` (int), `solution` (string);
    - additional columns allowed only for local experiments and must be dropped before Kaggle submit.
  - `submission/autosubmit.py`:
    - validates the schema;
    - submits via Kaggle CLI with HTTP fallback;
    - logs events to `autosubmit.log`.
- Minimal baselines:
  - `generate_dummy_submission.py`:
    - reads `test.csv`;
    - produces a trivially valid `submission.csv` (empty `solution`);
    - runs local validation.

### 2. Solver architecture

- Search-based scaffold:
  - `search/moves.py` – canonical move alphabet and string↔list helpers.
  - `search/solver_random_beam.py`:
    - `SearchConfig` controls max depth, beam width, branching, seed;
    - `solve_instance` / `solve_batch` generate move sequences / solution strings;
    - pluggable heuristic function (currently a stub, designed to accept richer features and NN guidance).
  - `solve_with_search.py`:
    - assumes `test.csv` has columns `id` and `state` (ASSUMPTION);
    - builds `submission_search.csv` using the search scaffold.
- NN + search hybrid scaffolding:
  - `nn/schema.py` – `StateTensorSpec` / `TargetSpec` and default specs.
  - `nn/interfaces.py` – `PolicyValueModel` protocol, `NNGuidedHeuristic` adapter, `num_moves()` helper.
  - `docs/05_NN_HYBRID_SOLVER_PLAN.md` – design for integrating trained NN models as heuristics/policies inside search.

### 3. Experiment workflow & runners

- Runners:
  - `run_experiment.py`:
    - `--mode dummy` → `submission_dummy.csv`;
    - `--mode search` → `submission_search.csv`.
  - `run_best.py`:
    - currently runs the search scaffold and writes `submission_best.csv`;
    - intended to track the strongest validated configuration over time.
- Workflow docs:
  - `docs/06_EXPERIMENT_WORKFLOW.md` describes:
    - how to prepare data;
    - how to choose modes and generate submission-like files;
    - how to integrate with `submission/autosubmit.py`;
    - how to log experiments in line with root standards.

### 4. Open engineering directions

Short list of next engineering steps (to be detailed in future work):

- Plug a real 4×4×4 engine behind the `search` interfaces (state simulation, solved checks).
- Implement stronger heuristics informed by `docs/04_POTENTIAL_HYPOTHESES.md` (metrics/invariants).
- Connect a trained NN (via `PolicyValueModel`) to `NNGuidedHeuristic` and compare search-only vs NN-guided performance.

