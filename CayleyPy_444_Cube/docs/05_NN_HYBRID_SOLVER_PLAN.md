## NN + search hybrid plan for CayleyPy-444-Cube

> **Status:** high-level plan and scaffolding.  
> Concrete training code and heavy NN frameworks are intentionally not included yet.

### 1. Roles of NN components

- **Policy head** (optional on first iterations):
  - Input: tensorized cube state.
  - Output: scores / logits over the move alphabet defined in `search/moves.py` (`ALL_MOVES`).
  - Use: bias move selection inside search (beam search, MCTS, guided IDA*).
- **Value head**:
  - Input: tensorized cube state.
  - Output: scalar estimate of \"goodness\" (e.g. negative distance-to-go or probability of solving within a given depth).
  - Use: define a heuristic score for search, trade off with length penalty.

The initial target is a **value-focused model**; policy can be added later.

### 2. Interface layer (this repo)

- `nn/schema.py`:
  - `StateTensorSpec` – describes how a cube state will be represented as a tensor (channels, height, width, optional metadata).
  - `TargetSpec` – describes prediction targets (policy size, presence of value head).
  - `default_state_tensor_spec()` / `default_target_spec()` – placeholder specs that must be refined once a concrete encoding and move set are finalized.
- `nn/interfaces.py`:
  - `PolicyValueModel` protocol – minimal interface for any NN that outputs `(policy_scores, value_estimate)` given a `state_repr: str`.
  - `NNGuidedHeuristic` – adapter that turns a `PolicyValueModel` into a heuristic function compatible with `search.solver_random_beam`.
  - `num_moves()` – reports the size of the move alphabet (`len(ALL_MOVES)`).

These modules define *shapes and contracts* without committing to a specific ML library.

### 3. Integration with search

- Current search entry points:
  - `search/solver_random_beam.solve_instance(state_repr, config, heuristic)`  
  - `search/solver_random_beam.solve_batch(states, config, heuristic)`
- To plug NN guidance into search:
  1. Implement a concrete `PolicyValueModel` (e.g. in a separate training project) that:
     - reads `state_repr` strings and converts them to tensors according to `StateTensorSpec`;
     - returns `(policy_scores, value_estimate)` compatible with `num_moves()`.
  2. Instantiate `NNGuidedHeuristic(model=...)`.
  3. Pass this heuristic into `solve_instance` / `solve_batch`.

At this stage, the repo only contains the adapter code; training and model definitions should live in a dedicated ML environment.

### 4. Data and training (out of scope for now)

- **Data sources** (to be implemented in a training-specific project):
  - trajectories from search-only solvers (state → good move / value);
  - logs from strong handcrafted solvers or external references (if available);
  - synthetic scrambles with known solutions for supervised pretraining.
- **Training tasks**:
  - value regression: predict normalized solution length or success probability;
  - optional policy learning: imitate good move distributions.

This subproject should only assume that, after training, there exists a model conforming to `PolicyValueModel` which can be imported and used at inference time.

### 5. Next concrete steps for NN + search

- Decide on a canonical state encoding and finalize `StateTensorSpec`.
- Implement a thin wrapper that:
  - locates a trained NN model (e.g. from a sibling project);
  - exposes it as a `PolicyValueModel` instance.
- Run small-scale experiments comparing:
  - pure search with handcrafted heuristics;
  - NN-guided search (same compute budget).

Results and design decisions from these experiments should be documented alongside `docs/04_POTENTIAL_HYPOTHESES.md`, especially where NN guidance interacts with metric / invariant hypotheses.

