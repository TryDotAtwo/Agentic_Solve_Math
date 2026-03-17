from __future__ import annotations

from .organization import OrganizationModel


def callable_targets(org: OrganizationModel, agent_id: str) -> tuple[str, ...]:
    manifest = org.get_agent(agent_id)
    return manifest.callable_agents
