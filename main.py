from __future__ import annotations

"""
Root launcher for the Agentic Solve Math meta-orchestrator.

The root level is responsible for:
- discovering isolated subprojects;
- parsing root-level Kaggle intake files;
- delegating execution into local subproject entry points;
- keeping the workspace readable and reproducible;
- launching the live root multi-agent runtime when OpenAI bootstrap settings are present.

Backwards compatibility:
- if the script is called with only option-like arguments, they are forwarded
  to `CayleyPy_444_Cube/main.py` as a legacy convenience path.

Default behavior:
- `python main.py` launches the default root operator session if `OPENAI_API_KEY`
  or a root `.env` file is present;
- the operator session starts the browser dashboard and the live root runtime
  under one terminal-controlled process;
- otherwise it falls back to the root overview/CLI surface.
"""

import sys

from workspace_orchestrator.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
