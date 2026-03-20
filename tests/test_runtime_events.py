from pathlib import Path

from workspace_orchestrator.runtime_events import append_runtime_event, build_dialogue_feed, load_runtime_events


def test_runtime_events_are_appended_and_dialogue_feed_filters_latest_entries(tmp_path: Path) -> None:
    root = tmp_path

    append_runtime_event(
        root,
        event_type="tool_called",
        title="Tool start",
        summary="Root Orchestrator called build_handoff.",
        scope="root",
        session_id="root-main",
        team_id="root:root",
        agent_id="root.orchestrator",
        agent_name="Root Orchestrator",
    )
    append_runtime_event(
        root,
        event_type="memory_note_recorded",
        title="Memory updated",
        summary="A private note was recorded.",
        scope="root",
        session_id="root-main",
        team_id="root:root",
        agent_id="root.06_editorial_and_history.history_scribe",
        agent_name="History Scribe",
    )
    append_runtime_event(
        root,
        event_type="agent_message",
        title="Agent message",
        summary="Research department summarized the latest findings.",
        scope="root",
        session_id="root-main",
        team_id="root:root",
        agent_id="root.02_research_intelligence.head",
        agent_name="Research Intelligence Head",
        transcript="We should validate the baseline before opening a new experiment branch.",
    )

    events = load_runtime_events(root, limit=10)
    dialogue = build_dialogue_feed(root, limit=10)

    assert len(events) == 3
    assert events[-1].event_type == "agent_message"
    assert len(dialogue) == 2
    assert dialogue[0]["event_type"] == "agent_message"
    assert dialogue[1]["event_type"] == "tool_called"
