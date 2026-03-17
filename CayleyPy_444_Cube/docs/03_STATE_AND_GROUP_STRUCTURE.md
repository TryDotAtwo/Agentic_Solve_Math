## 03 – State and group structure for CayleyPy-444-Cube

> **Status:** conceptual draft focused on mathematical structure.  
> Items explicitly marked **ASSUMPTION** must be checked against the official competition spec and baseline code once available.

### 1. State space: what is a “state”?

- **Known from docs**
  - The competition revolves around scrambled configurations of a \(4 \times 4 \times 4\) Rubik’s cube (a “4×4×4 cube”).  
  - Submissions provide **move sequences** that transform each scrambled state, and the evaluation script checks whether the cube is solved after applying them.

- **State representation (ASSUMPTION)**
  - A *state* is a configuration of all physical pieces of a 4×4×4 cube:
    - 8 corner cubies (each with 3 stickers),
    - 24 edge cubies (paired into 12 edge positions in the solved state),
    - 24 center cubies (4 per face, no fixed centers as in 3×3×3).
  - Mathematically, a state can be modeled as:
    - a **permutation** of cubies together with
    - an **orientation** assignment on corners and edges,
    - plus the arrangement of center pieces into face colors.
  - In many cube libraries, this is encoded as a combined structure:
    - corners: permutation in \(S_8\) with orientation in \(\mathbb{Z}_3^8\),
    - edges: permutation in \(S_{24}\) with orientation in \(\mathbb{Z}_2^{24}\),
    - centers: permutation in \(S_{24}\) partitioned into 6 color classes of 4.

- **Constraints on physically reachable states (ASSUMPTION)**
  - Not every formal assignment of permutations/orientations corresponds to a physically reachable state. Physical moves respect:
    - **parity constraints** on permutations (e.g. correlation between corner, edge, and center permutations),
    - **orientation sums** (e.g. total corner twist modulo 3 equals 0; total edge flip parity is constrained),
    - compatibility of colorings for centers (only certain permutations preserve the overall coloring pattern).
  - The **state space of the competition** is expected to be a subset of physically reachable states; scrambles are assumed to start from the solved state and apply legal moves only.

### 2. Underlying group and Cayley graph

#### 2.1. The group (ASSUMPTION)

- Let \(G\) denote the group of all physically reachable configurations of the 4×4×4 cube under the allowed moves.
- Elements of \(G\) are **states** as described above; the group operation is **composition of moves** (i.e. applying one sequence after another).
- The **identity element** is the solved cube.
- In theory, \(G\) is a subgroup of the full permutation group of all stickers, constrained by:
  - fixed color pattern constraints,
  - parity and orientation constraints from physical move mechanics.

#### 2.2. Generators and move set

- **Known / strongly suggested by docs**
  - Solutions are sequences of *moves* written in a notation similar to standard cube notation (`R`, `L`, `U`, `D`, `F`, `B`, with modifiers, and likely wide moves like `Rw`, `Lw`).

- **Generator set (ASSUMPTION)**
  - Let \(S\) be a finite set of generators corresponding to the **basic face and slice turns** of the 4×4×4 cube:
    - outer face quarter-turns: `R`, `L`, `U`, `D`, `F`, `B` and their inverses,
    - wide turns (two-layer moves): `Rw`, `Lw`, `Uw`, `Dw`, `Fw`, `Bw`,
    - possibly half-turns `X2` treated either as primitives or as `X X`.
  - Every legal move sequence in the competition is a word in the alphabet \(S \cup S^{-1}\).  
  - The exact move set (e.g. inclusion of inner slice moves, rotation moves) must be deduced from the official rules or reference implementation.

#### 2.3. Cayley graph perspective

- Given a generating set \(S\), the **Cayley graph** \(\Gamma(G, S)\) is defined by:
  - **vertices**: all states \(g \in G\),
  - **edges**: for each generator \(s \in S\) and each \(g \in G\), an edge between \(g\) and \(g s\).
- In this perspective:
  - A scrambled cube state corresponds to some vertex \(g_{\text{scr}}\).
  - The solved state is the identity vertex \(e\).
  - A solution sequence of moves is a path in \(\Gamma(G, S)\) from \(g_{\text{scr}}\) to \(e\).
  - The **length** of the sequence is the number of edges (moves) on that path.

### 3. Metrics on the state space

- **Natural word metric (ASSUMPTION)**
  - Define the **distance** \(d(g, h)\) between two states \(g, h \in G\) as the minimal number of moves from the allowed generator set \(S\) needed to transform \(g\) into \(h\).
  - For the competition, the primary case of interest is \(d(g_{\text{scr}}, e)\), the minimal solution length (in moves) from a scramble to the solved state.
  - This metric is directly aligned with the expected **competition score** (sum or mean of move counts), up to constants and possible penalties.

- **Weighted metrics (ASSUMPTION)**
  - Some move types (e.g. inner slice moves vs outer face turns) might be assigned different costs, either:
    - by the competition scoring (if specified), or
    - by our internal heuristics (e.g. giving extra penalty to complex moves).
  - In that case, the Cayley graph can be considered as a **weighted graph**, and distances become minimal weighted path lengths.

### 4. Relationship to competition I/O formats

- **Known from docs**
  - The competition inputs likely provide some encoding of states (e.g. `state` or `facelets` column).
  - The submission file contains a `solution` column with a sequence of moves.

- **Mapping between formats and group elements (ASSUMPTION)**
  - There will be an **internal representation** of cube states (e.g. a Python object with permutation/orientation fields) and a **string representation** used in CSV files.
  - A parsing pipeline is expected:
    - string from CSV → internal state object in \(G\),
    - internal move tokens → elements of the generator set \(S\),
    - simulation of moves: starting from input state, apply generators to reach the solved state.
  - For mathematical analysis, we assume:
    - there exists a fixed, canonical solved state \(e\),
    - all input states are reachable from \(e\) by composing generators from \(S\),
    - the evaluation script checks that applying the submitted move sequence to the input state yields \(e\).

### 5. Assumptions, unknowns, and future clarifications

- **Explicit assumptions to be checked later**
  - Exact definition of the allowed move set \(S\) (which moves are allowed, and how they are notated).
  - Whether the scoring metric is:
    - pure **move count**, or
    - a **weighted** move cost (e.g. slices vs wide turns vs rotations).
  - Whether there are explicit **upper bounds** on solution length or constraints on move sequences (e.g. maximum length, forbidden patterns).
  - Exact **data encoding** for states and move sequences in CSV files.

- **Future links to math-hypothesis lab**
  - Once the exact group presentation and move set are known, this document can be:
    - enriched with a more formal description of \(G\) (generators, relations),
    - connected to generic tools in the math-hypothesis lab for:
      - analyzing Cayley graphs,
      - exploring subgroup structure,
      - constructing and testing heuristics based on group-theoretic invariants.

