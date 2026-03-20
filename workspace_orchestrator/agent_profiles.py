from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .organization import (
    AgentManifest,
    OrganizationModel,
    build_root_organization,
    build_subproject_organization,
)


@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    display_name: str
    scope: str
    department_key: str
    rank: str
    private_root: Path
    memory_file: Path
    instructions_file: Path
    rules_file: Path
    reports_file: Path


def ensure_root_agent_profiles(root: Path) -> dict[str, AgentProfile]:
    return ensure_organization_agent_profiles(build_root_organization(root))


def ensure_subproject_agent_profiles(root: Path, subproject_name: str) -> dict[str, AgentProfile]:
    return ensure_organization_agent_profiles(build_subproject_organization(root, subproject_name))


def ensure_agent_profile(root: Path, agent_id: str) -> AgentProfile:
    organization = _organization_for_agent(root, agent_id)
    return ensure_organization_agent_profiles(organization)[agent_id]


def ensure_organization_agent_profiles(organization: OrganizationModel) -> dict[str, AgentProfile]:
    profiles: dict[str, AgentProfile] = {}
    for manifest in organization.agents:
        _ensure_profile_files(manifest)
        profiles[manifest.agent_id] = AgentProfile(
            agent_id=manifest.agent_id,
            display_name=manifest.display_name,
            scope=manifest.scope,
            department_key=manifest.department_key,
            rank=manifest.rank,
            private_root=manifest.private_profile_root,
            memory_file=manifest.memory_file,
            instructions_file=manifest.instructions_file,
            rules_file=manifest.rules_file,
            reports_file=manifest.reports_file,
        )
    return profiles


def append_private_memory_note(
    root: Path,
    agent_id: str,
    title: str,
    body: str,
    tags: tuple[str, ...] = (),
) -> Path:
    profile = ensure_agent_profile(root, agent_id)
    tag_line = f"Tags: {', '.join(tags)}" if tags else "Tags: -"
    section = "\n".join(
        (
            "",
            f"## {_utc_now()} | {title}",
            tag_line,
            "",
            body.strip(),
            "",
        )
    )
    with profile.memory_file.open("a", encoding="utf-8") as handle:
        handle.write(section)
    return profile.memory_file


def append_department_milestone(
    root: Path,
    agent_id: str,
    title: str,
    summary: str,
    next_actions: tuple[str, ...] = (),
) -> Path:
    profile = ensure_agent_profile(root, agent_id)
    if profile.rank != "head":
        raise ValueError(f"Milestones may only be authored by department heads, got {agent_id}")

    section_lines = [
        "",
        f"## {_utc_now()} | {title}",
        f"Agent: {profile.agent_id}",
        f"Department: {profile.department_key}",
        f"Scope: {profile.scope}",
        "",
        "Summary:",
        summary.strip(),
        "",
        "Next actions:",
    ]
    if next_actions:
        section_lines.extend(f"- {item}" for item in next_actions)
    else:
        section_lines.append("- No explicit next actions recorded.")
    section_lines.append("")
    with profile.reports_file.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(section_lines))
    return profile.reports_file


def collect_department_milestones(root: Path, limit: int = 12) -> list[dict[str, object]]:
    roots = [
        root / ".agent_workspace" / "agent_profiles",
        *sorted(root.glob("*/.agent_workspace/agent_profiles")),
    ]
    milestones: list[dict[str, object]] = []
    for profiles_root in roots:
        if not profiles_root.exists():
            continue
        for reports_path in profiles_root.rglob("reports.md"):
            milestones.extend(_parse_reports_file(reports_path))
    milestones.sort(key=lambda item: str(item["created_at"]), reverse=True)
    return milestones[:limit]


def profile_excerpt(path: Path, limit: int = 220) -> str:
    if not path.exists():
        return ""
    lines = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
        if len(" ".join(lines)) >= limit:
            break
    excerpt = " ".join(lines)
    return excerpt[:limit] + ("..." if len(excerpt) > limit else "")


def _organization_for_agent(root: Path, agent_id: str) -> OrganizationModel:
    root = root.resolve()
    if agent_id.startswith("root."):
        return build_root_organization(root)
    if agent_id.startswith("subproject."):
        parts = agent_id.split(".")
        if len(parts) < 3:
            raise ValueError(f"Cannot infer subproject from agent id: {agent_id}")
        return build_subproject_organization(root, parts[1])
    raise ValueError(f"Unsupported agent id: {agent_id}")


def _ensure_profile_files(manifest: AgentManifest) -> None:
    manifest.private_profile_root.mkdir(parents=True, exist_ok=True)
    _write_if_missing(manifest.instructions_file, _default_instructions_text(manifest))
    _write_if_missing(manifest.rules_file, _default_rules_text(manifest))
    _write_if_missing(manifest.memory_file, _default_memory_text(manifest))
    _write_if_missing(manifest.reports_file, _default_reports_text(manifest))


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def _default_instructions_text(manifest: AgentManifest) -> str:
    return "\n".join(
        (
            f"# {manifest.display_name}",
            "",
            "## Role",
            f"- Agent ID: `{manifest.agent_id}`",
            f"- Scope: `{manifest.scope}`",
            f"- Department: `{manifest.department_key}`",
            f"- Rank: `{manifest.rank}`",
            "",
            "## Mission",
            "- Execute only the responsibilities assigned to this role.",
            "- Respect visibility boundaries and interact through approved agent links.",
            "- Keep durable notes in `memory.md` and publish notable progress to `reports.md` when appropriate.",
            "",
            "## Operational Surface",
            f"- Allowed tools: {', '.join(manifest.allowed_tools) or '-'}",
            f"- Callable agents: {', '.join(manifest.callable_agents) or '-'}",
            f"- Shared services: {', '.join(manifest.shared_service_agents) or '-'}",
            "",
        )
    )


def _default_rules_text(manifest: AgentManifest) -> str:
    return "\n".join(
        (
            f"# {manifest.display_name} Rules",
            "",
            "## Hierarchy",
            f"- Executive link surface: `{', '.join(manifest.callable_agents) or '-'}`",
            "- Escalate policy, scope, or architecture conflicts instead of bypassing the chain of command.",
            "",
            "## Visibility",
            f"- Read roots: {', '.join(str(item) for item in manifest.read_roots) or '-'}",
            f"- Hidden roots: {', '.join(str(item) for item in manifest.hidden_roots) or '-'}",
            "",
            "## Write Authority",
            f"- Writable targets: {', '.join(str(item) for item in manifest.write_roots) or '-'}",
            f"- Mutable rule roots: {', '.join(str(item) for item in manifest.mutable_rule_roots) or '-'}",
            "",
            "## Reporting",
            "- Private memory lives in `memory.md` and should capture durable local context.",
            "- Department heads should record user-facing milestones in `reports.md`.",
            "",
        )
    )


def _default_memory_text(manifest: AgentManifest) -> str:
    return "\n".join(
        (
            f"# {manifest.display_name} Memory",
            "",
            "This file stores durable private working memory for the owning agent.",
            "",
        )
    )


def _default_reports_text(manifest: AgentManifest) -> str:
    return "\n".join(
        (
            f"# {manifest.display_name} Reports",
            "",
            "User-facing milestones and department-level progress updates belong here.",
            "",
        )
    )


def _parse_reports_file(path: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    title: str | None = None
    metadata: dict[str, str] = {}
    summary_lines: list[str] = []
    next_actions: list[str] = []
    mode = ""

    def flush() -> None:
        nonlocal title, metadata, summary_lines, next_actions, mode
        if title is None:
            return
        timestamp, clean_title = _split_timestamped_title(title)
        entries.append(
            {
                "created_at": timestamp,
                "title": clean_title,
                "agent_id": metadata.get("Agent", ""),
                "department_key": metadata.get("Department", ""),
                "scope": metadata.get("Scope", ""),
                "summary": " ".join(line.strip() for line in summary_lines if line.strip()),
                "next_actions": tuple(item for item in next_actions if item),
                "source": str(path),
            }
        )
        title = None
        metadata = {}
        summary_lines = []
        next_actions = []
        mode = ""

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            flush()
            title = raw_line[3:].strip()
            continue
        if title is None:
            continue
        line = raw_line.strip()
        if not line:
            continue
        if line in {"Summary:", "Next actions:"}:
            mode = line
            continue
        if line.startswith("Agent:"):
            metadata["Agent"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Department:"):
            metadata["Department"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Scope:"):
            metadata["Scope"] = line.split(":", 1)[1].strip()
            continue
        if mode == "Summary:":
            summary_lines.append(line)
            continue
        if mode == "Next actions:" and line.startswith("- "):
            next_actions.append(line[2:].strip())
    flush()
    return entries


def _split_timestamped_title(value: str) -> tuple[str, str]:
    if " | " not in value:
        return "", value
    timestamp, title = value.split(" | ", 1)
    return timestamp.strip(), title.strip()


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
