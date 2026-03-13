## Autosubmit setup for CayleyPy-444-Cube

> **Goal**: provide a minimal, reliable **autosubmit pipeline** for the CayleyPy-444-Cube competition that:
>
> - validates the local submission CSV format;
> - submits via **Kaggle CLI** when available;
> - falls back to **HTTP API** if CLI is broken (following the Pancake project’s `main.py` pattern);
> - logs attempts and responses for reproducibility.

This document only specifies design and usage.  
Implementation lives under `submission/` inside this subproject.

### 1. Module layout

Target layout inside `CayleyPy_444_Cube/`:

```text
CayleyPy_444_Cube/
  README.md
  docs/
    01_COMPETITION_OVERVIEW.md
    02_AUTOSUBMIT_SETUP.md
  submission/
    __init__.py
    autosubmit.py
  tests/
    test_submission_format.py
```

- `submission/autosubmit.py`:
  - single, self-contained module responsible for:
    - loading a submission CSV;
    - validating its schema and basic types;
    - submitting via Kaggle CLI, with an HTTP fallback;
    - writing simple logs to a file.
- `tests/test_submission_format.py`:
  - tiny smoke test that:
    - builds a dummy DataFrame with the expected columns;
    - runs the local validation function (no network).

### 2. Assumed competition slug and configuration

- **Assumed Kaggle competition slug**: `cayleypy-444-cube` (**TODO: verify**).
- **Default competition** used in code:
  - `DEFAULT_KAGGLE_COMPETITION = "cayleypy-444-cube"` (to be updated once the real slug is known).
- Environment / CLI overrides:
  - Environment variable: `KAGGLE_COMPETITION` (takes precedence over default).
  - Command-line flag: `--competition` (overrides both default and env).

All of this is confined to `submission/autosubmit.py` so it is easy to change in one place.

### 3. Python API design

`submission/autosubmit.py` exposes a small, clear API:

- **Loading & validation**

  ```python
  from pathlib import Path
  from CayleyPy_444_Cube.submission.autosubmit import (
      load_submission_csv,
      validate_submission_schema,
  )

  df = load_submission_csv(Path("submission.csv"))
  validate_submission_schema(df)
  ```

  - `load_submission_csv(path: Path) -> pd.DataFrame`
    - Reads a CSV file, raises `SystemExit` or `ValueError` with a clear message if:
      - the file does not exist;
      - the file cannot be parsed as CSV.
  - `validate_submission_schema(df: pd.DataFrame) -> None`
    - Checks:
      - that columns `id` and `solution` exist;
      - that `id` is integer-like and has no duplicates;
      - that `solution` is present and string-like (non-null for basic cases).
    - Raises `ValueError` on schema or type problems.

- **Submission**

  ```python
  from CayleyPy_444_Cube.submission.autosubmit import submit_file

  submit_file(
      file_path="submission.csv",
      competition=None,  # use env or default
      message="baseline test submit",
  )
  ```

  - `submit_file(file_path: str | Path, competition: str | None, message: str | None) -> None`
    - Validates the file path and CSV structure;
    - Resolves competition slug (flag → env → default);
    - Tries Kaggle CLI first, then HTTP fallback;
    - Logs attempts and responses into a local log file in the project root (e.g. `autosubmit.log`).

### 4. Command-line usage

`submission/autosubmit.py` is also directly executable:

```bash
python -m CayleyPy_444_Cube.submission.autosubmit \ 
    --file submission.csv \
    --competition cayleypy-444-cube \
    --message "first test submit"
```

Command-line arguments (implemented in the module):

- `--file` (default: `submission.csv`)
  - Path to the submission CSV file to upload.
- `--competition`, `-c` (default: env `KAGGLE_COMPETITION` or hardcoded default)
  - Kaggle competition slug.
- `--message`, `-m` (default: empty string)
  - Submission description shown on Kaggle.

This is intentionally simpler than the full Pancake CLI; the heavy lifting (search, solving, experiments) lives elsewhere.

### 5. Kaggle CLI submission flow

The CLI submission path mirrors the Pancake project’s logic, adapted for this subproject:

1. Resolve `file_path` to an absolute `Path`.
2. Check that the file exists; if not, raise `SystemExit` with a clear error message.
3. Determine `competition`:
   - if provided argument is non-empty, use it;
   - else if `KAGGLE_COMPETITION` env var is set, use that;
   - else use `DEFAULT_KAGGLE_COMPETITION`.
4. Check for a `kaggle` executable:
   - Use `shutil.which("kaggle")`.
   - On Windows, also check `Path(sys.executable).parent / "Scripts" / "kaggle.exe"`.
5. Build the CLI command:

   ```text
   kaggle competitions submit -c <competition> -f <file_path> -m <message>
   ```

   If no `kaggle` executable is found, fall back to:

   ```text
   python -m kaggle competitions submit -c <competition> -f <file_path> -m <message>
   ```

6. Run the command via `subprocess.run(...)`:
   - Capture stdout / stderr.
   - On success (return code 0), print a friendly message and log the event.
   - On failure, inspect stderr:
     - If the error suggests a **kagglesdk** / token misconfiguration, proceed to HTTP fallback.
     - Otherwise, raise `SystemExit` with a helpful message.

### 6. HTTP fallback (no CLI or broken CLI)

The HTTP fallback is heavily inspired by Pancake’s `_kaggle_submit_http`:

1. Look for `kaggle.json` in the following directories (in order):
   - `KAGGLE_CONFIG_DIR` env var (if set);
   - project root (`CayleyPy_444_Cube` directory);
   - `~/.kaggle/`.
2. If no `kaggle.json` is found, abort with instructions:
   - Download from Kaggle settings (`API → Create New Token`).
   - Place it in `~/.kaggle/kaggle.json` or in this project’s root.
3. Parse `kaggle.json` as JSON, expecting:
   - `username`
   - `key`
4. Build HTTP request:
   - URL: `https://www.kaggle.com/api/v1/competitions/submit/<competition>`.
   - Authentication: Basic auth with `username:key` base64‑encoded.
   - Method: `POST` multipart/form-data:
     - `submission`: `(file_name, file_obj, "text/csv")`
     - `description`: the message (or file name).
5. Send the request with `requests.post` and a reasonable timeout (e.g. 120 seconds).
6. Handle response codes:
   - `200`: print success message and log the event.
   - `404`: explain that the legacy HTTP API may no longer be supported and instruct to fix CLI.
   - Any other code: raise `SystemExit` with status code and a text snippet.

### 7. Logging

Simple logging is performed by appending JSON lines to `autosubmit.log` in the subproject root:

- Each entry is a single JSON object, something like:

  ```json
  {
    "timestamp": 1710000000.0,
    "event": "kaggle_cli_submit",
    "file": "submission.csv",
    "competition": "cayleypy-444-cube",
    "success": true,
    "details": "CLI returned 0"
  }
  ```

- Logged events include:
  - `schema_validation_ok` / `schema_validation_failed`
  - `kaggle_cli_submit` (with success / failure info)
  - `kaggle_http_submit` (with response status code)

No personal credentials are logged; only the presence and location of `kaggle.json` is mentioned implicitly through success/failure.

### 8. Minimal local test

`tests/test_submission_format.py` contains a tiny smoke test that:

- constructs a dummy DataFrame:

  ```python
  import pandas as pd
  from CayleyPy_444_Cube.submission.autosubmit import validate_submission_schema

  def test_dummy_submission_schema_ok():
      df = pd.DataFrame(
          {
              "id": [1, 2, 3],
              "solution": ["R2 U2", "Lw' F2", ""],
          }
      )
      validate_submission_schema(df)  # should not raise
  ```

- is intended to be run via pytest or any test runner configured by the root project (this subagent does not enforce a particular choice).

This ensures that:

- the validation logic is importable and behaves as documented; and
- the rest of the autosubmit code can safely assume a consistent schema.

