from __future__ import annotations

from pathlib import Path

from .organization import AgentManifest


def can_read_path(agent: AgentManifest, path: Path) -> bool:
    target = path.resolve(strict=False)
    if _is_hidden(agent, target):
        return False
    return _is_under_any(target, agent.read_roots)


def can_write_path(agent: AgentManifest, path: Path) -> bool:
    target = path.resolve(strict=False)
    if _is_hidden(agent, target):
        return False
    return _is_under_any(target, agent.write_roots)


def _is_hidden(agent: AgentManifest, target: Path) -> bool:
    return _is_under_any(target, agent.hidden_roots)


def _is_under_any(target: Path, roots: tuple[Path, ...]) -> bool:
    return any(_is_within(target, root.resolve(strict=False)) for root in roots)


def _is_within(target: Path, root: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False
