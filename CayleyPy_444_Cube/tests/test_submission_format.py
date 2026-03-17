import pandas as pd

from CayleyPy_444_Cube.submission.autosubmit import validate_submission_schema


def test_dummy_submission_schema_ok() -> None:
    """Smoke test: a minimal dummy submission passes local validation."""
    df = pd.DataFrame(
        {
            "initial_state_id": [0, 1, 2],
            "path": ["f1", "-d3.-r3", ""],
        }
    )

    # Should not raise
    validate_submission_schema(df)

