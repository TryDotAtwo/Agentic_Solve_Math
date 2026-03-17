## CayleyPy-444-Cube – Competition overview

> **Status:** draft, based on assumptions.  
> All items marked **TODO** or **ASSUMPTION** must be verified against the official Kaggle page when available.
>
> **Current hard interface contract (for code and autosubmit)**
>
> - Competition slug used in code: `cayleypy-444-cube` (can be overridden via `--competition` CLI флага или env `KAGGLE_COMPETITION`; см. `submission/autosubmit.py`).  
> - Minimal submission schema, на которой завязан валидатор и автосабмит:
>   - колонка `id` (целочисленный идентификатор экземпляра, без пропусков и дубликатов);
>   - колонка `solution` (строка с последовательностью ходов, допускается пустая строка как \"нет решения\").  
> - Любые дополнительные столбцы (например, `score_estimate`, `method`) считаются **внутренними** и должны быть отброшены перед финальным Kaggle‑сабмитом, если соревнование явно не разрешает их в submission‑файле.
>
> Эти пункты задают **жёсткий интерфейс** между кодом генерации `submission.csv`, локальным валидатором и модулем автосабмита. При первом ручном чтении официальной страницы соревнования человек‑оператор должен:
>
> - подтвердить или скорректировать competition slug;
> - проверить, что Kaggle действительно ожидает ровно столбцы `id` и `solution` (или явно задать отличия);
> - при расхождениях обновить как этот документ, так и `submission/autosubmit.py` и тест `tests/test_submission_format.py`.

### 1. Problem brief

- **Competition name**: *CayleyPy-444-Cube* (exact Kaggle slug is assumed to be `cayleypy-444-cube`, to be confirmed).  
- **Assumed URL**: `https://www.kaggle.com/competitions/cayleypy-444-cube` (**TODO: verify**).
- **Informal description (ASSUMPTION)**:
  - Input data contains scrambled configurations of a \(4 \times 4 \times 4\) Rubik’s cube.
  - For each instance, the participant must output a sequence of moves that solves the cube (reaches the solved state).
  - The competition is likely part of the broader CayleyPy series, focusing on hard search problems in group theory / combinatorics.

#### 1.1. Objective and scoring (ASSUMPTION)

- **Objective**: minimize the total cost of solving all cubes in the test set.
- **Cost / metric**:
  - The *primary* score is assumed to be the sum (or mean) of move counts across all instances:
    \[
    \text{score} = \sum_i \text{cost}(\text{solution}_i)
    \]
  - The cost of a single solution is assumed to be proportional to the number of moves in the sequence (possibly with a fixed offset / penalty for invalid or missing solutions).
  - A lower score is better.

These assumptions mirror the design of the *CayleyPy-pancake* competition and must be confirmed in the official rules.

### 2. Data and state representation (ASSUMPTION)

The exact data format is not yet known. Below is a **best-guess** structure, intended only as a starting point for local tooling.

#### 2.1. Train / test inputs

Likely CSV files with at least:

- `id` – unique integer identifier for each scrambled cube.
- One of:
  - `state` – a textual encoding of the 4×4×4 cube state; or
  - `permutation` – a permutation of stickers / cubies, or
  - `facelets` – a string listing face colors (e.g. `"UUUU...RRRR...FFFF..."`).

**ASSUMPTION**: Use a single column named `state` for now, encoded as a string.  
The precise encoding (e.g. facelet notation, cube group generators, etc.) is unknown and must be synchronized with the baseline solver once available.

Example (illustrative only):

```text
id,state
1,"UURR... (encoding TBD)"
2,"..."
```

#### 2.2. Additional metadata columns (optional / TBD)

- `length_bound` – an optional bound on the allowed move sequence length. (**TODO: check**)
- `scramble_id` – ID of the scramble pattern or difficulty bucket. (**TODO: check**)

These are speculative and should not be relied on until the actual schema is known.

### 3. Submission format

> This section defines the **expected schema** for the submission CSV used by the autosubmit tooling.  
> Where the official spec is not yet known, we explicitly mark assumptions and TODOs.

#### 3.1. Required columns

**Minimal submission schema (ASSUMPTION):**

- `id` – integer, matching exactly the `id` column from the competition’s test set.
- `solution` – string, encoding a sequence of cube moves that solves the instance.

This mirrors the pattern used in CayleyPy-Pancake (`id,solution`) and is the simplest viable schema for autosubmit.

Examples (purely illustrative; move notation TBD):

```text
id,solution
1,"Rw U2 Rw' F2 ..."
2,"..."
```

**Notes:**

- The order of rows does not matter for Kaggle, as long as all `id` values are present and unique.
- Missing or duplicated `id`s will almost certainly cause the submission to be rejected or scored as poor.

#### 3.2. Column types and validation rules (ASSUMPTION)

- `id`
  - Type: integer (Python `int`, Pandas `Int64` / `int64`).
  - Must be unique.
  - Must match the set of IDs in the official test file.
- `solution`
  - Type: non-empty string for solved instances; may be empty for unsolved (interpretation TBD).
  - Encoding: sequence of moves in a given notation.
    - Likely to use a variant of standard cube notation: `R`, `L`, `U`, `D`, `F`, `B`, with modifiers (`'`, `2`) and inner turns specifically for 4×4×4 (e.g. `Rw`, `Lw`).
    - The delimiter between moves is assumed to be a space `" "` or period `"."`.  
      (**TODO: confirm actual delimiter and parse rules**.)

The local submission validation utility in `submission/autosubmit.py` will:

- check that `id` and `solution` columns exist;
- check that `id` is integer-like and has no duplicates;
- optionally check for obviously invalid `solution` entries (e.g. nulls, non-string types).

#### 3.3. Optional / extended columns (ASSUMPTION)

We keep the **core** submission contract minimal (`id,solution`).  
However, internal experiments may use additional columns such as:

- `score_estimate` – approximate cost of the solution (e.g. number of moves).
- `method` – label of the solver used to generate the solution.

These columns:

- should be **stripped out** or **dropped** before final Kaggle submission, unless the competition explicitly allows them;
- may be preserved in local logs and research tables.

### 4. Evaluation internals (ASSUMPTION)

While the exact evaluation script is unknown, we assume:

- Kaggle converts the submitted `solution` into a list of moves.
- It applies each move sequence to the corresponding initial cube state from the test set.
- It checks whether the cube is solved within a maximum allowed number of moves.
  - If solved:
    - Add the cost (likely number of moves) to the total score.
  - If unsolved / invalid:
    - Either assign a large penalty (e.g. treat as maximum length), or reject the submission.

The **key implication** for engineering:

- The autosubmit pipeline only needs to **guarantee the presence and basic type correctness** of `id` and `solution`.  
- **Semantic correctness** (e.g. does the sequence actually solve the cube?) is a **solver-side** responsibility, not an autosubmit concern.

### 5. What must be reconstructed on evaluation side

From the official perspective (Kaggle’s hidden evaluation), the platform must reconstruct:

- The full cube state for each `id` from the private test data.
- The effect of each move in the participant’s `solution` sequence on that state.
- The final state after all moves are applied.

From the **local research / engineering** perspective, we should:

- Maintain a consistent representation of cube states and moves between:
  - training / development code;
  - local evaluation scripts (if any);
  - submission generation code.
- Clearly document the mapping between:
  - the string format in `solution`; and
  - the internal move objects / group elements used in solvers.

These details will be fleshed out when the first baseline solvers for CayleyPy-444-Cube are implemented.

