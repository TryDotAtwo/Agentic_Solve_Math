import runpy
from pathlib import Path


def test_root_main_propagates_cli_exit_code(monkeypatch) -> None:
    main_path = Path(__file__).resolve().parent.parent / "main.py"

    monkeypatch.setattr("workspace_orchestrator.cli.main", lambda: 7)

    try:
        runpy.run_path(str(main_path), run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 7
    else:
        raise AssertionError("Expected main.py to raise SystemExit with the CLI exit code.")
