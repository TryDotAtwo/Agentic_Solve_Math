## Experiment workflow for CayleyPy-444-Cube

> **Status:** initial scaffold aligned with root `EXPERIMENT_LOGGING_STANDARD.md`.

### 1. Entry points for experiments

- `run_experiment.py`
  - CLI wrapper that can:
    - run the **dummy baseline**:
      - calls `generate_dummy_submission` (empty solutions);
      - writes `submission_dummy.csv` (or a user-specified path);
    - run the **search-based solver scaffold**:
      - calls `generate_search_submission`;
      - writes `submission_search.csv` (or a user-specified path).
- `run_best.py`
  - Convenience wrapper for the current \"best known\" configuration:
    - runs `generate_search_submission(test.csv -> submission_best.csv)`.
- `submission/autosubmit.py`
  - Handles validation + actual Kaggle submission when the user is ready.

### 2. Typical local experiment loop

1. **Prepare data**
   - Ensure `test.csv` (and, when needed, train/validation subsets) are present in the project root.
2. **Choose a solver configuration**
   - For quick checks, use:
     - `python run_experiment.py --mode dummy`
     - `python run_experiment.py --mode search`
   - As stronger solvers appear (better heuristics, NN-guided search), extend `run_experiment.py` with new modes.
3. **Generate a submission-like file**
   - Inspect the resulting `submission_*.csv`:
     - shape and columns (`id`, `solution`);
     - basic sanity (no NaNs, extremely long strings, etc.).
4. **Validate and (optionally) submit**
   - Use `submission/autosubmit.py` to:
     - re-validate the schema;
     - send the file to Kaggle when you want a leaderboard score.

### 3. Logging and comparison

In line with root standards:

- For each significant experiment, record in the local docs (e.g. `docs/04_POTENTIAL_HYPOTHESES.md` or a dedicated results file):
  - solver configuration (mode, search parameters, heuristic/NN version);
  - where the submission file is stored;
  - Kaggle score (if submitted) and any offline metrics;
  - short narrative conclusion (hypothesis supported / rejected / needs more work).
- For cross-session summary and scientific traceability, add condensed notes to the root `RESEARCH_JOURNAL.md` when:
  - a new solver family is introduced;
  - a significant score improvement is achieved;
  - a nontrivial hypothesis about metrics / invariants / NN guidance is updated.

