# Submission guide – CayleyPy-444-Cube

## Quick start

From the workspace root (`D:\Agentic_Solve_Math`):

```powershell
cd CayleyPy_444_Cube
python main.py --no-download-data --no-submit   # Generate only (no Kaggle)
python main.py --no-download-data               # Generate + submit to Kaggle
python main.py                                  # Download + generate + submit
```

## Prerequisites

1. **Data**  
   `data/test.csv` must exist. Either:
   - run `main.py` without `--no-download-data` (downloads via Kaggle CLI), or
   - copy competition data manually into `data/`.

2. **Kaggle API** (needed for download + submit)  
   Kaggle CLI and credentials are required:
   - Install: `pip install kaggle`
   - Create token: Kaggle → Account → API → Create New Token
   - Place `kaggle.json` in one of:
     - `CayleyPy_444_Cube/` (project root)
     - `~/.kaggle/kaggle.json`  
   - Fallback: `kaggle (1).json` in project root is also accepted.

## What the solver does

- **Engine**: Uses `data/puzzle_info.json` for generators and state encoding (96 positions).
- **Search**: Two-stage beam search:
  - Stage 1: fast pass (beam 256, depth 25) on all instances.
  - Stage 2: re-solve suspected hard instances (beam 1024, depth 40).
- **Output**: `submission_best.csv` with columns `initial_state_id` and `path` (dot-separated move strings).

## Validation before submit

```powershell
python CayleyPy_444_Cube\run_best.py   # Generates submission_best.csv
# Schema is validated automatically when you submit via main.py or autosubmit.
python -m CayleyPy_444_Cube.submission.autosubmit --file submission_best.csv -m "test"
# ^ This will validate and submit; omit to only generate with --no-submit.
```

## Submit manually via Kaggle CLI

```powershell
kaggle competitions submit -c cayley-py-444-cube -f CayleyPy_444_Cube\submission_best.csv -m "State-aware beam search"
```

## Troubleshooting

- **"Could not find kaggle.json"**  
  Ensure `kaggle.json` exists in `CayleyPy_444_Cube/` or `~/.kaggle/`. Rename `kaggle (1).json` if needed.

- **"Submission contains null values in 'path' column"**  
  The solver should no longer produce nulls. If it occurs, run with `--no-submit` and inspect `submission_best.csv`.

- **Slow run**  
  ~1000 instances with beam search can take several minutes. Use `--no-download-data` when data is already present.
