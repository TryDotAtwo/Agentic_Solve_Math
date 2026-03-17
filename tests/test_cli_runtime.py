import json
from pathlib import Path

from workspace_orchestrator import cli


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    intake_dir = tmp_path / "kaggle_intake"
    intake_dir.mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube").mkdir()
    (intake_dir / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
- https://arxiv.org/abs/1234.5678
""",
        encoding="utf-8",
    )
    return tmp_path


def test_build_handoff_command_materializes_run(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _prepare_root(tmp_path)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    exit_code = cli.main(
        [
            "build-handoff",
            "--project",
            "CayleyPy_444_Cube",
            "--objective",
            "Investigate the competition",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    run_dir = Path(payload["run_dir"])

    assert exit_code == 0
    assert payload["target_agent_id"] == "subproject.CayleyPy_444_Cube.commander"
    assert run_dir.exists()
    assert (run_dir / "handoff.json").exists()


def test_record_result_and_show_run_commands_use_root_owned_run_dir(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = _prepare_root(tmp_path)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    cli.main(
        [
            "build-handoff",
            "--project",
            "CayleyPy_444_Cube",
            "--objective",
            "Investigate the competition",
            "--json",
        ]
    )
    build_payload = json.loads(capsys.readouterr().out)
    run_id = build_payload["run_id"]

    exit_code = cli.main(
        [
            "record-result",
            run_id,
            "--produced-by",
            "subproject.CayleyPy_444_Cube.commander",
            "--status",
            "completed",
            "--summary",
            "Research summary prepared.",
            "--canonical-path",
            "CayleyPy_444_Cube/docs/research_summary.md",
            "--json",
        ]
    )
    result_payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert result_payload["status"] == "completed"

    exit_code = cli.main(["show-run", run_id, "--json"])
    show_payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert show_payload["trace"]["status"] == "completed"
    assert show_payload["result"]["summary"] == "Research summary prepared."
