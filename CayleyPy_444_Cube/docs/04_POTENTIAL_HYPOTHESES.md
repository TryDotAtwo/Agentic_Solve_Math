## 04 – Potential hypotheses for CayleyPy-444-Cube

> **Status:** brainstorming draft for hypothesis‑driven work.  
> All hypotheses below are **tentative** and require empirical testing or deeper mathematical analysis.  
> Each item includes: ID, formulation, intuition, and a sketch of how to test it.

### 1. Metric and heuristic hypotheses

- **ID:** `H4C_metric_1` – Layered distance approximation
  - **Formulation:**  
    The true distance to the solved state can be usefully approximated by a **sum of layerwise distances** (e.g. centers, edge pairing, 3×3 reduction, final solve), possibly with learned weights.
  - **Why it might be true/useful (intuition):**  
    Many human and algorithmic methods for 4×4×4 proceed in phases: first fix centers, then pair edges, then solve like a 3×3×3. The independent (or weakly coupled) nature of these subtasks suggests that a decomposed metric may correlate well with the actual optimal distance.
  - **Evidence / experiments needed:**  
    - Implement a phase-based representation of states.  
    - For a sample of scrambles, compute:
      - minimal or approximate move counts to complete each phase,
      - the total optimal/near‑optimal solution length.  
    - Measure correlation between phase-sum distance estimates and true solution lengths.

- **ID:** `H4C_metric_2` – Admissible pattern-database style heuristics
  - **Formulation:**  
    Restricted **pattern databases (PDBs)** for subsets of cubies (e.g. centers only, edge pairs only) yield **admissible** heuristics that are strong enough to guide search on nontrivial instances within competition time budgets.
  - **Why it might be true/useful (intuition):**  
    On other combinatorial puzzles (e.g. 3×3×3 cube, 15‑puzzle, pancake variants), PDBs capturing a subset of features significantly reduce search spaces while preserving admissibility. Similar substructures exist for 4×4×4 (centers, edge pairs, parity patterns).
  - **Evidence / experiments needed:**  
    - Define small or compressed PDBs for selected subcomponents.  
    - Integrate them into IDA*/A* or related search on a subset of instances.  
    - Compare node expansions and runtime vs. weaker heuristics (e.g. simple move counts, random playout estimates).

- **ID:** `H4C_metric_3` – Difficulty concentrated near parity / last-layer anomalies
  - **Formulation:**  
    Instances with **edge parity** or other last-layer anomalies (e.g. unsimplified edge pairs) are significantly further from the solved state, on average, than parity-free instances with similar superficial disorder.
  - **Why it might be true/useful (intuition):**  
    On 4×4×4, special parity cases often require dedicated sequences (“parity algorithms”) that add a constant but nontrivial overhead to solution length. States without such anomalies might admit shorter or more straightforward completions.
  - **Evidence / experiments needed:**  
    - Define features that detect parity / anomaly configurations.  
    - For a large sample of scrambles, categorize them by parity features.  
    - Estimate solution length (by strong heuristics or near‑optimal search) and compare distributions between parity and non‑parity groups.

### 2. Invariants and decomposition hypotheses

- **ID:** `H4C_invariant_1` – Phase invariants decouple subproblems
  - **Formulation:**  
    There exist **invariants** (e.g. parity vectors, orientation sums, center pattern signatures) that remain stable under large classes of moves, allowing the state space to be decomposed into relatively independent **layers** or **subspaces** (centers, edges, corners).
  - **Why it might be true/useful (intuition):**  
    Many standard 4×4×4 methods restrict to move sets that affect only certain cubie types (e.g. inner slice moves that modify centers and edges but keep overall face orientation stable). If certain invariants localize the effect of moves, one can design specialized search modules on lower‑dimensional factors.
  - **Evidence / experiments needed:**  
    - Define candidate invariants (e.g. parity of edge flips, corner twist sum, center color pattern signatures).  
    - Empirically track how they change under different move subsets.  
    - Verify which invariants are preserved under restricted generators and whether this yields useful factorization of the Cayley graph.

- **ID:** `H4C_invariant_2` – Subgroup structure mirrors solving phases
  - **Formulation:**  
    The natural solving phases (fix centers, pair edges, reduce to 3×3, solve) correspond to increasing chains of subgroups  
    \[
    H_0 \le H_1 \le H_2 \le G,
    \]
    where each \(H_i\) encodes constraints satisfied after phase \(i\), and moves used within a phase generate (or approximate) that subgroup.
  - **Why it might be true/useful (intuition):**  
    If solving phases correspond to subgroup inclusions, one can reason about reachable states and optimal paths within smaller subgroups, then stitch them together. This may simplify both proof‑style reasoning and algorithm design.
  - **Evidence / experiments needed:**  
    - Formalize constraints defining each phase (e.g. “centers solved” as a property of the state).  
    - Identify move sets that leave these constraints invariant.  
    - Check closure and subgroup properties empirically or via enumeration on smaller projected state spaces.

- **ID:** `H4C_invariant_3` – Edge-pairing as a lower‑dimensional factor
  - **Formulation:**  
    The process of **pairing edges** can be modeled in a lower‑dimensional state space where each pair is a single object, and moves induce a (smaller) group action on these objects; solving in this factor can be treated separately from full‑cube orientation details.
  - **Why it might be true/useful (intuition):**  
    A large portion of 4×4×4 complexity stems from edge pairing. If this task can be abstracted as a simpler combinatorial system with its own Cayley graph, search in that factor may be more tractable and still informative for the full problem.
  - **Evidence / experiments needed:**  
    - Define an abstraction in which each edge pair is a single “piece” with limited orientations.  
    - Simulate how standard moves act on this abstraction.  
    - Measure whether distances in this reduced space correlate with full‑cube distances.

### 3. Hard instance and distributional hypotheses

- **ID:** `H4C_hard_1` – Competition scrambles avoid pathological extremes
  - **Formulation:**  
    The distribution of scrambles in the competition is biased away from **extremely long** or “God’s distance” states, making moderate‑depth search combined with good heuristics sufficient for strong leaderboard performance.
  - **Why it might be true/useful (intuition):**  
    For practical reasons (evaluation time, fairness), organizers often avoid extremely hard instances. If true, then investing heavily in exact optimal solvers may have diminishing returns compared to robust near‑optimal methods.
  - **Evidence / experiments needed:**  
    - Approximate distances to the solved state for many training/test scrambles using strong heuristics.  
    - Compare their distribution to known or estimated diameters / lower bounds for the 4×4×4 cube.  
    - Check for truncated tails or conspicuous absence of very long‑distance states.

- **ID:** `H4C_hard_2` – Structural signatures of hard scrambles
  - **Formulation:**  
    Certain **local structural features** (e.g. mixed center patterns, dispersed edge pairs, multiple interacting parities) are predictive of higher search complexity and longer required solutions.
  - **Why it might be true/useful (intuition):**  
    In other combinatorial puzzles, specific motifs (e.g. “almost solved but with parity”) make instances disproportionately hard. If similar motifs can be identified for 4×4×4, they can guide curriculum strategies, adaptive time allocation, or specialized sub‑solvers.
  - **Evidence / experiments needed:**  
    - Define feature extractors for scrambles (parity indicators, number of correctly placed centers, edge‑pairing score, etc.).  
    - For each instance, record both features and achieved solution lengths under a fixed solver.  
    - Train simple models or compute correlations to see which features best predict difficulty.

### 4. Connections and contrasts with the Pancake problem

- **ID:** `H4C_vs_Pancake_1` – Local vs global move structure
  - **Formulation:**  
    Compared to the **pancake problem**, moves on the 4×4×4 cube are more *local* and structured (face turns, slice turns) rather than global prefix reversals; this may make **local heuristics** (based on nearby configuration) more reliable than in pancake.
  - **Why it might be true/useful (intuition):**  
    In pancake, a single flip can drastically change many positions; on the cube, moves typically affect a limited set of pieces in a patterned way. This could allow for more localized, compositional heuristics and invariants.
  - **Evidence / experiments needed:**  
    - Define comparable local features for both problems (e.g. number of “misplaced” items under local criteria).  
    - Compare how much these features change per move and how predictive they are of true distance in each domain.

- **ID:** `H4C_vs_Pancake_2` – Subgroup and phase analogues of prefix‑flip layers
  - **Formulation:**  
    The 4×4×4 cube’s natural subgroup/phase decomposition (centers, edges, 3×3 reduction) plays a role analogous to **partial prefix sorting** layers in pancake; techniques for analyzing **layer‑by‑layer progress** may be transferable between the two problems.
  - **Why it might be true/useful (intuition):**  
    In pancake, many strategies reason about “how many of the first \(k\) pancakes are already in place”. On 4×4×4, similar notions arise (how many centers fixed, how many edges paired, how many last‑layer pieces solved). Concepts like **progress measures** and **layer potentials** might carry over.
  - **Evidence / experiments needed:**  
    - Formalize analogous progress measures in both domains.  
    - Study their evolution under typical solving algorithms and random moves.  
    - Check whether shared “progress” patterns correlate with solution length or branching complexity.

### 5. Interfaces to the math-hypothesis lab

- **ID:** `H4C_lab_1` – Generic Cayley-graph tools as shared infrastructure
  - **Formulation:**  
    The 4×4×4 cube can serve as a concrete testbed for **generic Cayley‑graph analysis tools** (e.g. exploration of growth rates, isoperimetric profiles, random walks) developed in the broader math‑hypothesis lab, with insights flowing in both directions.
  - **Why it might be true/useful (intuition):**  
    Many structural questions (growth functions, mixing times, diameter bounds) appear both in abstract group theory and in practical puzzle solving. A well‑instrumented 4×4×4 environment connects experimental evidence to theoretical conjectures.
  - **Evidence / experiments needed:**  
    - Implement reusable components for random walks, sphere sampling (sets of states at fixed distance), and small subgraph enumeration.  
    - Compare empirical measurements with theoretical expectations or bounds (where available).

- **ID:** `H4C_lab_2` – Transfer of heuristics across CayleyPy problems
  - **Formulation:**  
    Certain heuristic‑construction patterns (e.g. pattern databases, additive decompositions, progress‑based potentials) discovered in CayleyPy‑pancake experiments can be **translated** to the 4×4×4 group with limited adaptation.
  - **Why it might be true/useful (intuition):**  
    Both tasks involve search on large Cayley graphs with structured generators. Abstracting away the details (flips vs face turns), many heuristic ideas depend only on having a group action and a notion of cost.
  - **Evidence / experiments needed:**  
    - Catalogue successful heuristic designs from pancake.  
    - For each, attempt to define an analogue on the 4×4×4 cube (possibly via different feature maps).  
    - Benchmark performance on small instance sets to see which ideas transfer well.

