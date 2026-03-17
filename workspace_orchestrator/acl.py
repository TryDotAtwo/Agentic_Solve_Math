from __future__ import annotations

from .organization import AgentManifest


def can_call_agent(caller: AgentManifest, callee: AgentManifest) -> bool:
    if caller.agent_id == callee.agent_id:
        return False
    return callee.agent_id in caller.callable_agents
