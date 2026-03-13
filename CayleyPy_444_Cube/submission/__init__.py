"""
Submission utilities for the CayleyPy-444-Cube competition.

This package currently exposes the autosubmit helper module:

- load_submission_csv
- validate_submission_schema
- submit_file

See docs/02_AUTOSUBMIT_SETUP.md for design and usage details.
"""

from .autosubmit import (  # noqa: F401
    load_submission_csv,
    validate_submission_schema,
    submit_file,
)

