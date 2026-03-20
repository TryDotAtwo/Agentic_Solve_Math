import json
from pathlib import Path
from urllib.request import urlopen

from workspace_orchestrator.dashboard_server import start_dashboard_server


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    logs_dir = tmp_path / "rules" / "logs"
    logs_dir.mkdir()
    (logs_dir / "RESEARCH_JOURNAL.md").write_text("# Research Journal\n", encoding="utf-8")
    (logs_dir / "AGENT_INTERACTIONS_LOG.md").write_text("# Agent Interactions Log\n", encoding="utf-8")
    (logs_dir / "USER_PROMPTS_LOG.md").write_text("# User Prompts Log\n", encoding="utf-8")
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    project_dir = tmp_path / "CayleyPy_TestHarness"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('fixture')\n", encoding="utf-8")
    (project_dir / "README.md").write_text("# Fixture project\n", encoding="utf-8")
    (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    return tmp_path


def test_dashboard_server_serves_html_and_json(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    handle = start_dashboard_server(root, host="127.0.0.1", port=0, run_limit=8, log_limit=4)

    try:
        with urlopen(f"{handle.url}/", timeout=5) as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert "Agentic Solve Math Observatory" in html
            assert "/assets/app_v3.js" in html
            assert "topology-stage" in html
            assert "topology-toolbar" in html
            assert "topology-focus" in html
            assert "topology-surface" in html
            assert "dialogue-list" in html
            assert "dialogue-detail" in html
            assert "activity-feed" in html

        with urlopen(f"{handle.url}/api/dashboard", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert payload["root_team"]["manager"]["agent_id"] == "root.orchestrator"

        with urlopen(f"{handle.url}/assets/app_v3.js", timeout=5) as response:
            script = response.read().decode("utf-8")
            assert response.status == 200
            assert "renderDashboard" in script
            assert "computeRadialGraphLayout" in script
            assert "renderTopologyStage" in script
            assert "buildDialogueThreads" in script
            assert "buildDialogueFocusState" in script
            assert "renderDialogueConsole" in script
            assert "chat-bubble__kind" in script
    finally:
        handle.close()
