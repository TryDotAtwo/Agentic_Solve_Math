from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import tomllib


RUNTIME_CONFIG_FILENAME = "runtime_config.toml"
GOOGLE_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENROUTER_OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
G4F_DEFAULT_BASE_URL = "http://127.0.0.1:1337/v1"
G4F_DEFAULT_HEALTHCHECK_URL = "http://127.0.0.1:1337/v1/models"

DEFAULT_OPENROUTER_FREE_MODELS = (
    "stepfun/step-3.5-flash:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
)


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def load_root_env(root: Path) -> dict[str, str]:
    values = parse_env_file(root / ".env")
    merged = dict(values)
    for key, value in os.environ.items():
        merged[key] = value
    return merged


def env_value(root: Path, key: str, default: str | None = None) -> str | None:
    values = load_root_env(root)
    return values.get(key, default)


@dataclass(frozen=True)
class RoleModelMatrix:
    manager: str
    research: str
    coding: str
    audit: str
    history: str
    support: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class LaunchConfig:
    max_turns: int = 12
    auto_install: bool = True
    open_browser: bool = True
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8765
    dashboard_run_limit: int = 12
    dashboard_log_limit: int = 8

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class OpenAIProviderConfig:
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str = ""
    default_model: str = ""
    role_models: RoleModelMatrix = field(
        default_factory=lambda: RoleModelMatrix(
            manager="gpt-5.2",
            research="gpt-5.2",
            coding="gpt-5.2-codex",
            audit="gpt-5.2",
            history="gpt-5-mini",
            support="gpt-5-mini",
        )
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "api_key_env": self.api_key_env,
            "base_url": self.base_url,
            "default_model": self.default_model,
            "models": self.role_models.to_dict(),
        }


@dataclass(frozen=True)
class OpenRouterProviderConfig:
    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = OPENROUTER_OPENAI_BASE_URL
    model_strategy: str = "free_pool"
    default_model: str = ""
    refresh_free_models: bool = True
    free_models_catalog_url: str = "https://openrouter.ai/api/v1/models"
    free_model_ids: tuple[str, ...] = DEFAULT_OPENROUTER_FREE_MODELS
    use_multi_provider: bool = True
    openai_prefix_mode: str = "model_id"
    unknown_prefix_mode: str = "model_id"
    disable_tracing: bool = True
    role_models: RoleModelMatrix = field(
        default_factory=lambda: RoleModelMatrix(
            manager="openrouter/auto",
            research="openrouter/auto",
            coding="openrouter/auto",
            audit="openrouter/auto",
            history="openrouter/auto",
            support="openrouter/auto",
        )
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "api_key_env": self.api_key_env,
            "base_url": self.base_url,
            "model_strategy": self.model_strategy,
            "default_model": self.default_model,
            "refresh_free_models": self.refresh_free_models,
            "free_models_catalog_url": self.free_models_catalog_url,
            "free_model_ids": list(self.free_model_ids),
            "use_multi_provider": self.use_multi_provider,
            "openai_prefix_mode": self.openai_prefix_mode,
            "unknown_prefix_mode": self.unknown_prefix_mode,
            "disable_tracing": self.disable_tracing,
            "models": self.role_models.to_dict(),
        }


@dataclass(frozen=True)
class G4FProviderConfig:
    transport: str = "local_openai_compatible"
    base_url: str = G4F_DEFAULT_BASE_URL
    healthcheck_url: str = G4F_DEFAULT_HEALTHCHECK_URL
    client_api_key: str = "g4f-local"
    server_api_key_env: str = "G4F_API_KEY"
    auto_start_server: bool = True
    bind_host: str = "127.0.0.1"
    bind_port: int = 1337
    debug: bool = False
    startup_timeout_seconds: float = 20.0
    provider: str = ""
    default_model: str = "gpt-4o-mini"
    disable_tracing: bool = True
    role_models: RoleModelMatrix = field(
        default_factory=lambda: RoleModelMatrix(
            manager="gpt-4o-mini",
            research="gpt-4o-mini",
            coding="gpt-4o-mini",
            audit="gpt-4o-mini",
            history="gpt-4o-mini",
            support="gpt-4o-mini",
        )
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "transport": self.transport,
            "base_url": self.base_url,
            "healthcheck_url": self.healthcheck_url,
            "client_api_key": self.client_api_key,
            "server_api_key_env": self.server_api_key_env,
            "auto_start_server": self.auto_start_server,
            "bind_host": self.bind_host,
            "bind_port": self.bind_port,
            "debug": self.debug,
            "startup_timeout_seconds": self.startup_timeout_seconds,
            "provider": self.provider,
            "default_model": self.default_model,
            "disable_tracing": self.disable_tracing,
            "models": self.role_models.to_dict(),
        }


@dataclass(frozen=True)
class RuntimeConfig:
    config_path: str
    active_provider: str = "openai"
    launch: LaunchConfig = field(default_factory=LaunchConfig)
    openai: OpenAIProviderConfig = field(default_factory=OpenAIProviderConfig)
    openrouter: OpenRouterProviderConfig = field(default_factory=OpenRouterProviderConfig)
    g4f: G4FProviderConfig = field(default_factory=G4FProviderConfig)

    def to_dict(self) -> dict[str, object]:
        return {
            "config_path": self.config_path,
            "active_provider": self.active_provider,
            "launch": self.launch.to_dict(),
            "providers": {
                "openai": self.openai.to_dict(),
                "openrouter": self.openrouter.to_dict(),
                "g4f": self.g4f.to_dict(),
            },
        }


@dataclass(frozen=True)
class G4FServiceSpec:
    base_url: str
    healthcheck_url: str
    auto_start_server: bool
    bind_host: str
    bind_port: int
    debug: bool
    startup_timeout_seconds: float
    provider: str | None
    default_model: str | None
    server_api_key: str | None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["server_api_key"] = "***" if self.server_api_key else None
        return payload


@dataclass(frozen=True)
class ResolvedProviderRuntime:
    provider_id: str
    route_label: str
    api_key: str | None
    base_url: str | None
    config_path: str
    model_strategy: str
    default_model: str | None
    role_models: RoleModelMatrix
    free_model_ids: tuple[str, ...] = field(default_factory=tuple)
    free_model_source: str = "config"
    refresh_free_models: bool = False
    free_models_catalog_url: str | None = None
    use_multi_provider: bool = False
    openai_prefix_mode: str = "openai"
    unknown_prefix_mode: str = "error"
    default_openai_api: str | None = None
    disable_tracing: bool = False
    g4f_service: G4FServiceSpec | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["api_key"] = "***" if self.api_key else None
        payload["has_api_key"] = bool(self.api_key)
        payload["role_models"] = self.role_models.to_dict()
        payload["g4f_service"] = self.g4f_service.to_dict() if self.g4f_service else None
        return payload


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_int(value: Any, default: int) -> int:
    if value in (None, ""):
        return default
    return int(value)


def _as_float(value: Any, default: float) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _role_models_from_payload(payload: dict[str, Any] | None, defaults: RoleModelMatrix) -> RoleModelMatrix:
    payload = payload or {}
    return RoleModelMatrix(
        manager=str(payload.get("manager", defaults.manager)),
        research=str(payload.get("research", defaults.research)),
        coding=str(payload.get("coding", defaults.coding)),
        audit=str(payload.get("audit", defaults.audit)),
        history=str(payload.get("history", defaults.history)),
        support=str(payload.get("support", defaults.support)),
    )


def load_runtime_config(root: Path) -> RuntimeConfig:
    config_path = root / RUNTIME_CONFIG_FILENAME
    payload: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("rb") as handle:
            payload = tomllib.load(handle)

    bootstrap_payload = payload.get("bootstrap", {}) or {}
    launch_payload = payload.get("launch", {}) or {}
    providers_payload = payload.get("providers", {}) or {}

    openai_defaults = OpenAIProviderConfig()
    openrouter_defaults = OpenRouterProviderConfig()
    g4f_defaults = G4FProviderConfig()

    openai_payload = providers_payload.get("openai", {}) or {}
    openrouter_payload = providers_payload.get("openrouter", {}) or {}
    g4f_payload = providers_payload.get("g4f", {}) or {}

    launch = LaunchConfig(
        max_turns=_as_int(launch_payload.get("max_turns"), 12),
        auto_install=_as_bool(launch_payload.get("auto_install"), True),
        open_browser=_as_bool(launch_payload.get("open_browser"), True),
        dashboard_host=str(launch_payload.get("dashboard_host", "127.0.0.1")),
        dashboard_port=_as_int(launch_payload.get("dashboard_port"), 8765),
        dashboard_run_limit=_as_int(launch_payload.get("dashboard_run_limit"), 12),
        dashboard_log_limit=_as_int(launch_payload.get("dashboard_log_limit"), 8),
    )

    openai = OpenAIProviderConfig(
        api_key_env=str(openai_payload.get("api_key_env", openai_defaults.api_key_env)),
        base_url=str(openai_payload.get("base_url", openai_defaults.base_url)),
        default_model=str(openai_payload.get("default_model", openai_defaults.default_model)),
        role_models=_role_models_from_payload(openai_payload.get("models"), openai_defaults.role_models),
    )

    openrouter = OpenRouterProviderConfig(
        api_key_env=str(openrouter_payload.get("api_key_env", openrouter_defaults.api_key_env)),
        base_url=str(openrouter_payload.get("base_url", openrouter_defaults.base_url)),
        model_strategy=str(openrouter_payload.get("model_strategy", openrouter_defaults.model_strategy)),
        default_model=str(openrouter_payload.get("default_model", openrouter_defaults.default_model)),
        refresh_free_models=_as_bool(
            openrouter_payload.get("refresh_free_models"),
            openrouter_defaults.refresh_free_models,
        ),
        free_models_catalog_url=str(
            openrouter_payload.get("free_models_catalog_url", openrouter_defaults.free_models_catalog_url)
        ),
        free_model_ids=tuple(
            str(item)
            for item in openrouter_payload.get("free_model_ids", openrouter_defaults.free_model_ids)
        ),
        use_multi_provider=_as_bool(
            openrouter_payload.get("use_multi_provider"),
            openrouter_defaults.use_multi_provider,
        ),
        openai_prefix_mode=str(
            openrouter_payload.get("openai_prefix_mode", openrouter_defaults.openai_prefix_mode)
        ),
        unknown_prefix_mode=str(
            openrouter_payload.get("unknown_prefix_mode", openrouter_defaults.unknown_prefix_mode)
        ),
        disable_tracing=_as_bool(
            openrouter_payload.get("disable_tracing"),
            openrouter_defaults.disable_tracing,
        ),
        role_models=_role_models_from_payload(openrouter_payload.get("models"), openrouter_defaults.role_models),
    )

    g4f = G4FProviderConfig(
        transport=str(g4f_payload.get("transport", g4f_defaults.transport)),
        base_url=str(g4f_payload.get("base_url", g4f_defaults.base_url)),
        healthcheck_url=str(g4f_payload.get("healthcheck_url", g4f_defaults.healthcheck_url)),
        client_api_key=str(g4f_payload.get("client_api_key", g4f_defaults.client_api_key)),
        server_api_key_env=str(g4f_payload.get("server_api_key_env", g4f_defaults.server_api_key_env)),
        auto_start_server=_as_bool(
            g4f_payload.get("auto_start_server"),
            g4f_defaults.auto_start_server,
        ),
        bind_host=str(g4f_payload.get("bind_host", g4f_defaults.bind_host)),
        bind_port=_as_int(g4f_payload.get("bind_port"), g4f_defaults.bind_port),
        debug=_as_bool(g4f_payload.get("debug"), g4f_defaults.debug),
        startup_timeout_seconds=_as_float(
            g4f_payload.get("startup_timeout_seconds"),
            g4f_defaults.startup_timeout_seconds,
        ),
        provider=str(g4f_payload.get("provider", g4f_defaults.provider)),
        default_model=str(g4f_payload.get("default_model", g4f_defaults.default_model)),
        disable_tracing=_as_bool(
            g4f_payload.get("disable_tracing"),
            g4f_defaults.disable_tracing,
        ),
        role_models=_role_models_from_payload(g4f_payload.get("models"), g4f_defaults.role_models),
    )

    return RuntimeConfig(
        config_path=str(config_path),
        active_provider=str(bootstrap_payload.get("active_provider", "openai")),
        launch=launch,
        openai=openai,
        openrouter=openrouter,
        g4f=g4f,
    )


def _active_provider_id(config: RuntimeConfig) -> str:
    override = os.environ.get("ASM_PROVIDER", "").strip().lower()
    if override:
        return override
    return config.active_provider.strip().lower()


def resolve_provider_runtime(root: Path, provider_override: str | None = None) -> ResolvedProviderRuntime:
    root = root.resolve()
    config = load_runtime_config(root)
    active_provider = (provider_override or _active_provider_id(config)).strip().lower()
    values = load_root_env(root)

    if active_provider == "openai":
        api_key = values.get(config.openai.api_key_env)
        base_url = config.openai.base_url or None
        route_label = "openai"
        if not api_key:
            google_key = values.get("GOOGLE_API_KEY") or values.get("GEMINI_API_KEY")
            if google_key:
                api_key = google_key
                base_url = GOOGLE_OPENAI_BASE_URL
                route_label = "google_openai_compatible"
        elif api_key.startswith("AIza"):
            base_url = GOOGLE_OPENAI_BASE_URL
            route_label = "google_openai_compatible"
        return ResolvedProviderRuntime(
            provider_id="openai",
            route_label=route_label,
            api_key=api_key,
            base_url=base_url,
            config_path=config.config_path,
            model_strategy="role_tiers",
            default_model=config.openai.default_model or None,
            role_models=config.openai.role_models,
            default_openai_api="chat_completions" if route_label == "google_openai_compatible" else None,
            disable_tracing=(route_label == "google_openai_compatible"),
        )

    if active_provider == "openrouter":
        free_models_override = os.environ.get("ASM_OPENROUTER_FREE_MODELS", "").strip()
        if free_models_override:
            free_model_ids = tuple(item.strip() for item in free_models_override.split(",") if item.strip())
            free_model_source = "env_override"
            refresh_free_models = False
        else:
            free_model_ids = config.openrouter.free_model_ids
            free_model_source = "config"
            refresh_free_models = config.openrouter.refresh_free_models
        return ResolvedProviderRuntime(
            provider_id="openrouter",
            route_label="openrouter",
            api_key=values.get(config.openrouter.api_key_env),
            base_url=config.openrouter.base_url,
            config_path=config.config_path,
            model_strategy=config.openrouter.model_strategy,
            default_model=config.openrouter.default_model or None,
            role_models=config.openrouter.role_models,
            free_model_ids=free_model_ids,
            free_model_source=free_model_source,
            refresh_free_models=refresh_free_models,
            free_models_catalog_url=config.openrouter.free_models_catalog_url,
            use_multi_provider=config.openrouter.use_multi_provider,
            openai_prefix_mode=config.openrouter.openai_prefix_mode,
            unknown_prefix_mode=config.openrouter.unknown_prefix_mode,
            default_openai_api="chat_completions",
            disable_tracing=config.openrouter.disable_tracing,
        )

    if active_provider == "g4f":
        server_api_key = values.get(config.g4f.server_api_key_env)
        service = G4FServiceSpec(
            base_url=config.g4f.base_url,
            healthcheck_url=config.g4f.healthcheck_url,
            auto_start_server=config.g4f.auto_start_server,
            bind_host=config.g4f.bind_host,
            bind_port=config.g4f.bind_port,
            debug=config.g4f.debug,
            startup_timeout_seconds=config.g4f.startup_timeout_seconds,
            provider=config.g4f.provider or None,
            default_model=config.g4f.default_model or None,
            server_api_key=server_api_key,
        )
        return ResolvedProviderRuntime(
            provider_id="g4f",
            route_label="g4f_local_openai_compatible",
            api_key=server_api_key or config.g4f.client_api_key,
            base_url=config.g4f.base_url,
            config_path=config.config_path,
            model_strategy="role_tiers",
            default_model=config.g4f.default_model or None,
            role_models=config.g4f.role_models,
            default_openai_api="chat_completions",
            disable_tracing=config.g4f.disable_tracing,
            g4f_service=service,
        )

    raise RuntimeError(
        f"Unsupported active provider `{active_provider}` in {config.config_path}. "
        "Expected one of: openai, openrouter, g4f."
    )


def _url_is_ready(url: str, timeout: float = 2.0) -> bool:
    request = Request(url, headers={"User-Agent": "AgenticSolveMath/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except (HTTPError, URLError, TimeoutError, ValueError):
        return False


def provider_bootstrap_available(root: Path, provider_override: str | None = None) -> bool:
    runtime = resolve_provider_runtime(root, provider_override=provider_override)
    if runtime.provider_id in {"openai", "openrouter"}:
        return bool(runtime.api_key)
    if runtime.provider_id == "g4f":
        if runtime.g4f_service and runtime.g4f_service.auto_start_server:
            return True
        if runtime.g4f_service:
            return _url_is_ready(runtime.g4f_service.healthcheck_url)
        return _url_is_ready(runtime.base_url or G4F_DEFAULT_HEALTHCHECK_URL)
    return False


def _price_is_zero(value: Any) -> bool:
    if value in (None, "", "null"):
        return False
    try:
        return float(str(value)) == 0.0
    except ValueError:
        return False


def discover_openrouter_free_models(catalog_url: str, timeout: float = 10.0) -> tuple[str, ...]:
    request = Request(catalog_url, headers={"User-Agent": "AgenticSolveMath/1.0"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    free_model_ids: list[str] = []
    seen: set[str] = set()
    for item in payload.get("data", ()):
        model_id = str(dict(item).get("id", "")).strip()
        if not model_id:
            continue
        pricing = dict(dict(item).get("pricing", {}) or {})
        price_values = [value for value in pricing.values() if value not in (None, "")]
        if not price_values:
            continue
        if not all(_price_is_zero(value) for value in price_values):
            continue
        free_id = model_id if model_id.endswith(":free") else f"{model_id}:free"
        if free_id in seen:
            continue
        seen.add(free_id)
        free_model_ids.append(free_id)
    return tuple(free_model_ids)


def _curated_catalog_intersection(
    curated_model_ids: tuple[str, ...],
    discovered_model_ids: tuple[str, ...],
) -> tuple[str, ...]:
    discovered = set(discovered_model_ids)
    return tuple(model_id for model_id in curated_model_ids if model_id in discovered)


def maybe_refresh_openrouter_runtime(runtime: ResolvedProviderRuntime) -> ResolvedProviderRuntime:
    if runtime.provider_id != "openrouter" or not runtime.refresh_free_models or not runtime.free_models_catalog_url:
        return runtime
    try:
        refreshed = discover_openrouter_free_models(runtime.free_models_catalog_url)
    except Exception:
        return runtime
    if not refreshed:
        return runtime
    curated = _curated_catalog_intersection(runtime.free_model_ids, refreshed)
    if not curated:
        return runtime
    return replace(runtime, free_model_ids=curated, free_model_source="catalog_intersection")


@dataclass
class ProviderSessionHandle:
    runtime: ResolvedProviderRuntime
    env_snapshot: dict[str, str | None]
    managed_process: subprocess.Popen[bytes] | None = None
    managed_stdout: object | None = None
    managed_stderr: object | None = None

    def close(self) -> None:
        if self.managed_process is not None:
            self.managed_process.terminate()
            try:
                self.managed_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.managed_process.kill()
                self.managed_process.wait(timeout=5)
        if self.managed_stdout is not None:
            self.managed_stdout.close()
        if self.managed_stderr is not None:
            self.managed_stderr.close()
        for key, previous in self.env_snapshot.items():
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous

    def __enter__(self) -> "ProviderSessionHandle":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _service_logs_dir(root: Path) -> Path:
    path = root / ".agent_workspace" / "services"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _start_g4f_service(root: Path, runtime: ResolvedProviderRuntime) -> ProviderSessionHandle:
    if runtime.g4f_service is None:
        raise RuntimeError("G4F runtime is missing service configuration.")
    service = runtime.g4f_service
    if _url_is_ready(service.healthcheck_url):
        return ProviderSessionHandle(runtime=runtime, env_snapshot={})

    if not service.auto_start_server:
        raise RuntimeError(
            "g4f provider is active but the local API is unavailable and auto_start_server=false. "
            f"Expected healthy endpoint: {service.healthcheck_url}"
        )

    logs_dir = _service_logs_dir(root)
    stdout_handle = (logs_dir / "g4f_stdout.log").open("a", encoding="utf-8")
    stderr_handle = (logs_dir / "g4f_stderr.log").open("a", encoding="utf-8")
    command = [
        sys.executable,
        "-c",
        (
            "from g4f.api import run_api; "
            f"run_api(host={service.bind_host!r}, port={service.bind_port!r}, debug={service.debug!r})"
        ),
    ]
    child_env = os.environ.copy()
    if service.server_api_key:
        child_env["G4F_API_KEY"] = service.server_api_key
    if service.provider:
        child_env["G4F_PROVIDER"] = service.provider
    if service.default_model:
        child_env["G4F_MODEL"] = service.default_model

    process = subprocess.Popen(
        command,
        cwd=str(root),
        env=child_env,
        stdout=stdout_handle,
        stderr=stderr_handle,
    )
    deadline = time.time() + service.startup_timeout_seconds
    while time.time() < deadline:
        if process.poll() is not None:
            stdout_handle.close()
            stderr_handle.close()
            raise RuntimeError(
                "g4f local API exited before becoming healthy. "
                f"See {logs_dir / 'g4f_stdout.log'} and {logs_dir / 'g4f_stderr.log'}."
            )
        if _url_is_ready(service.healthcheck_url):
            return ProviderSessionHandle(
                runtime=runtime,
                env_snapshot={},
                managed_process=process,
                managed_stdout=stdout_handle,
                managed_stderr=stderr_handle,
            )
        time.sleep(0.25)

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    stdout_handle.close()
    stderr_handle.close()
    raise RuntimeError(
        "g4f local API did not become healthy within the configured startup timeout. "
        f"Expected healthy endpoint: {service.healthcheck_url}"
    )


def activate_provider_runtime(root: Path, provider_override: str | None = None) -> ProviderSessionHandle:
    runtime = maybe_refresh_openrouter_runtime(resolve_provider_runtime(root, provider_override=provider_override))
    if runtime.provider_id == "openai" and not runtime.api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing for provider=openai. "
            "Put it in the environment or in the root .env file."
        )
    if runtime.provider_id == "openrouter" and not runtime.api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing for provider=openrouter. "
            "Put it in the environment or in the root .env file."
        )

    handle = ProviderSessionHandle(
        runtime=runtime,
        env_snapshot={
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
            "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL"),
            "ASM_ACTIVE_PROVIDER": os.environ.get("ASM_ACTIVE_PROVIDER"),
            "ASM_ACTIVE_PROVIDER_ROUTE": os.environ.get("ASM_ACTIVE_PROVIDER_ROUTE"),
        },
    )

    if runtime.provider_id == "g4f":
        service_handle = _start_g4f_service(root, runtime)
        handle.managed_process = service_handle.managed_process
        handle.managed_stdout = service_handle.managed_stdout
        handle.managed_stderr = service_handle.managed_stderr

    if runtime.api_key:
        os.environ["OPENAI_API_KEY"] = runtime.api_key
    else:
        os.environ.pop("OPENAI_API_KEY", None)
    if runtime.base_url:
        os.environ["OPENAI_BASE_URL"] = runtime.base_url
    else:
        os.environ.pop("OPENAI_BASE_URL", None)
    os.environ["ASM_ACTIVE_PROVIDER"] = runtime.provider_id
    os.environ["ASM_ACTIVE_PROVIDER_ROUTE"] = runtime.route_label
    return handle
