from __future__ import annotations

"""
Root launcher for the Agentic Solve Math meta-orchestrator.

The root level is responsible for:
- discovering isolated subprojects;
- parsing root-level Kaggle intake files;
- delegating execution into local subproject entry points;
- keeping the workspace readable and reproducible.

Backwards compatibility:
- if the script is called with only option-like arguments, they are forwarded
  to `CayleyPy_444_Cube/main.py` as a legacy convenience path.
"""

from workspace_orchestrator.cli import main


if __name__ == "__main__":
    main()
