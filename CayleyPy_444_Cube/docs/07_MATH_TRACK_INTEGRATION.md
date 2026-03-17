## Math track integration for CayleyPy-444-Cube

> **Status:** bridge between local math docs and the global math-hypothesis lab.

### 1. Local math documents in this subproject

- `docs/03_STATE_AND_GROUP_STRUCTURE.md`
  - Describes the conceptual state space and group structure of the 4×4×4 cube.
  - Defines assumptions about:
    - state representation (permutations + orientations + centers);
    - allowed move set and generators;
    - metrics (word metric, potential weighted variants).
- `docs/04_POTENTIAL_HYPOTHESES.md`
  - Contains hypothesis IDs (`H4C_metric_*`, `H4C_invariant_*`, `H4C_hard_*`, `H4C_vs_Pancake_*`, `H4C_lab_*`) with:
    - formulations;
    - intuition;
    - suggested experiments or analyses.

These two documents are the **local math anchor** for CayleyPy-444-Cube.

### 2. Linking experiments to hypotheses

When running experiments via:

- `run_experiment.py` / `run_best.py`;
- search-based solvers in `search/`;
- NN-guided solvers using `nn/interfaces.py`,

it is recommended to:

- explicitly reference hypothesis IDs from `docs/04_POTENTIAL_HYPOTHESES.md` when:
  - designing a new heuristic or feature set;
  - interpreting results that support or refute a hypothesis.
- record, for each nontrivial experiment:
  - which hypotheses it touches (e.g. `H4C_metric_1`, `H4C_hard_2`);
  - whether the evidence is:
    - `supports`, `contradicts`, or `inconclusive`;
  - links to logs, code versions, and (if applicable) Kaggle submissions.

This keeps the engineering and math views synchronized.

### 3. Path to the global math-hypothesis lab

For hypotheses that are:

- structural (group / Cayley-graph properties),
- cross-problem (shared with other CayleyPy competitions),
- or promising for formalization,

the intended workflow is:

1. **Promote** the local hypothesis:
   - create or update a corresponding card in the global math-hypothesis project (`Math_Hypothese_AutoCheck_Witch_Agents/`);
   - include:
     - the original ID (`H4C_*`);
     - a cleaned-up formulation;
     - a summary of computational evidence from this subproject.
2. **Connect**:
   - add a backlink from the global card to:
     - specific experiment logs / runs in this subproject;
     - relevant code modules (`search`, `nn`, solvers).
3. **Extend**:
   - in the math-hypothesis lab, pursue:
     - more abstract conjectures;
     - cross-problem analogues (e.g. Pancake vs 444-cube);
     - potential Lean-formalization routes.

### 4. Minimal discipline for math–engineering sync

- When a hypothesis from `docs/04_POTENTIAL_HYPOTHESES.md` is **substantially updated** (status change, strong evidence):
  - update that document with a brief status note;
  - if the hypothesis has a global counterpart, synchronize its status there as well;
  - add a short note to the root `RESEARCH_JOURNAL.md` describing:
    - what changed;
    - where to find the new evidence;
    - what this implies for future solver design.

This keeps the 444-cube subproject mathematically grounded and aligned with the broader research programme.

