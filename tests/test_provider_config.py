import json
import os
from pathlib import Path

from workspace_orchestrator.provider_config import (
    DEFAULT_OPENROUTER_FREE_MODELS,
    activate_provider_runtime,
    discover_openrouter_free_models,
    maybe_refresh_openrouter_runtime,
    provider_bootstrap_available,
    resolve_provider_runtime,
)


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    return tmp_path


def test_resolve_openrouter_runtime_uses_env_override_free_pool(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENROUTER_API_KEY=or-test-key\n", encoding="utf-8")
    monkeypatch.setenv("ASM_OPENROUTER_FREE_MODELS", "m1,m2,m3")

    runtime = resolve_provider_runtime(root, provider_override="openrouter")

    assert runtime.provider_id == "openrouter"
    assert runtime.api_key == "or-test-key"
    assert runtime.free_model_ids == ("m1", "m2", "m3")
    assert runtime.free_model_source == "env_override"
    assert runtime.refresh_free_models is False


def test_discover_openrouter_free_models_filters_zero_pricing(monkeypatch) -> None:
    payload = {
        "data": [
            {"id": "alpha/model-a", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "beta/model-b", "pricing": {"prompt": "0.001", "completion": "0"}},
            {"id": "gamma/model-c", "pricing": {"prompt": "0", "completion": "0", "image": "0"}},
        ]
    }

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr("workspace_orchestrator.provider_config.urlopen", lambda *args, **kwargs: _Response())

    model_ids = discover_openrouter_free_models("https://openrouter.ai/api/v1/models")

    assert model_ids == ("alpha/model-a:free", "gamma/model-c:free")


def test_maybe_refresh_openrouter_runtime_intersects_catalog_with_curated_pool(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENROUTER_API_KEY=or-test-key\n", encoding="utf-8")
    runtime = resolve_provider_runtime(root, provider_override="openrouter")

    monkeypatch.setattr(
        "workspace_orchestrator.provider_config.discover_openrouter_free_models",
        lambda url, timeout=10.0: (
            "fresh/model-a:free",
            DEFAULT_OPENROUTER_FREE_MODELS[-1],
            DEFAULT_OPENROUTER_FREE_MODELS[0],
            "fresh/model-b:free",
        ),
    )

    refreshed = maybe_refresh_openrouter_runtime(runtime)

    assert refreshed.free_model_ids == (
        DEFAULT_OPENROUTER_FREE_MODELS[0],
        DEFAULT_OPENROUTER_FREE_MODELS[-1],
    )
    assert refreshed.free_model_source == "catalog_intersection"


def test_maybe_refresh_openrouter_runtime_keeps_curated_pool_when_catalog_has_no_matches(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENROUTER_API_KEY=or-test-key\n", encoding="utf-8")
    runtime = resolve_provider_runtime(root, provider_override="openrouter")

    monkeypatch.setattr(
        "workspace_orchestrator.provider_config.discover_openrouter_free_models",
        lambda url, timeout=10.0: ("fresh/model-a:free", "fresh/model-b:free"),
    )

    refreshed = maybe_refresh_openrouter_runtime(runtime)

    assert refreshed.free_model_ids == runtime.free_model_ids
    assert refreshed.free_model_source == runtime.free_model_source


def test_provider_bootstrap_available_accepts_g4f_autostart_without_env(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)

    assert provider_bootstrap_available(root, provider_override="g4f") is True


def test_activate_provider_runtime_starts_and_restores_g4f_local_service(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    state = {"ready_calls": 0}

    def fake_ready(_url: str, timeout: float = 2.0) -> bool:
        state["ready_calls"] += 1
        return state["ready_calls"] > 1

    class FakeProcess:
        def __init__(self, *args, **kwargs):
            self._terminated = False

        def poll(self):
            return None

        def terminate(self):
            self._terminated = True

        def wait(self, timeout=None):
            return 0

        def kill(self):
            self._terminated = True

    monkeypatch.setattr("workspace_orchestrator.provider_config._url_is_ready", fake_ready)
    monkeypatch.setattr("workspace_orchestrator.provider_config.subprocess.Popen", FakeProcess)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    with activate_provider_runtime(root, provider_override="g4f") as session:
        assert session.runtime.provider_id == "g4f"
        assert os.environ["OPENAI_API_KEY"] == "g4f-local"
        assert os.environ["OPENAI_BASE_URL"] == "http://127.0.0.1:1337/v1"

    assert os.environ["OPENAI_API_KEY"] == "legacy-key"
