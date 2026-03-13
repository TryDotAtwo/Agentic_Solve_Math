import pandas as pd

from CayleyPy_444_Cube.submission.autosubmit import validate_submission_schema


def test_dummy_submission_schema_ok() -> None:
    """Smoke test: a minimal dummy submission passes local validation."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "solution": ["Rw U2", "Lw' F2", ""],
        }
    )

    # Should not raise
    validate_submission_schema(df)

