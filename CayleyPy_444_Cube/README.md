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

