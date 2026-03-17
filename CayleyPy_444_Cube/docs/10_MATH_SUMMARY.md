## Math summary – CayleyPy-444-Cube

> **Status:** canonical summary of local math structure and hypotheses for this subproject.

### 1. State and group structure (overview)

Based on `docs/03_STATE_AND_GROUP_STRUCTURE.md`:

- State space:
  - configurations of:
    - 8 corners (permutation + orientation);
    - 24 edges (paired into 12 edge positions, with orientations);
    - 24 centers (4 per face, with color pattern constraints).
  - physical constraints (parity, orientation sums, center patterns) restrict which formal states are reachable.
- Group and Cayley graph:
  - group \(G\) of physically reachable configurations under allowed moves;
  - generators (ASSUMPTION, to be confirmed with official rules and/or baseline code):
    - outer face turns (`R`, `L`, `U`, `D`, `F`, `B` and inverses/half-turns);
    - wide turns (`Rw`, `Lw`, `Uw`, `Dw`, `Fw`, `Bw` and variants);
  - Cayley graph \(\Gamma(G, S)\) with:
    - vertices = states;
    - edges = application of generators;
    - solution paths as shortest paths from scrambled states to the identity.
- Metrics:
  - natural word metric \(d(g, h)\) = minimal number of moves (or weighted moves);
  - competition score expected to correlate with sums of \(d(\text{scramble}_i, e)\).

### 2. Key local hypotheses

From `docs/04_POTENTIAL_HYPOTHESES.md` the most solver-relevant groups are:

- Metric/heuristic hypotheses (`H4C_metric_*`):
  - `H4C_metric_1` – layered/phase-wise distance approximation (centers, edges, 3×3 reduction, final solve).
  - `H4C_metric_2` – pattern-database style admissible heuristics on subsets (centers, edge pairs, parity patterns).
  - `H4C_metric_3` – difficulty concentrated near parity / last-layer anomalies.
- Invariant and decomposition hypotheses (`H4C_invariant_*`):
  - `H4C_invariant_1` – invariants that decouple subspaces (centers, edges, corners).
  - `H4C_invariant_2` – subgroup chains corresponding to solving phases.
  - `H4C_invariant_3` – edge-pairing as a lower-dimensional factor with its own Cayley graph.
- Hardness and distribution hypotheses (`H4C_hard_*`):
  - `H4C_hard_1` – competition scrambles avoid pathological extremes (easier than theoretical worst cases).
  - `H4C_hard_2` – identifiable structural signatures of hard scrambles.
- Cross-problem and lab integration (`H4C_vs_Pancake_*`, `H4C_lab_*`):
  - analogies with the pancake problem in terms of local vs global move structure and layered progress;
  - potential for shared Cayley-graph tools across CayleyPy competitions.

These IDs should be used when annotating experiments and designing new heuristics or NN features.

### 3. Integration with experiments and global math lab

- Local integration:
  - experiments that implement or test hypotheses should:
    - reference the relevant IDs (e.g. `H4C_metric_1`, `H4C_hard_2`);
    - record whether the evidence `supports`, `contradicts`, or is `inconclusive`;
    - link to specific runs, configurations, and logs.
  - see `docs/07_MATH_TRACK_INTEGRATION.md` for the recommended sync discipline.
- Global integration:
  - mature hypotheses, especially structural or cross-problem ones, should:
    - be promoted to the global math-hypothesis project (`Math_Hypothese_AutoCheck_Witch_Agents/`);
    - include summaries of computational evidence from this subproject;
    - be candidates for further theoretical work and potential Lean formalization.

