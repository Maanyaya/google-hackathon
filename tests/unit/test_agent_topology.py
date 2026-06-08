"""Agent structure tests — no LLM, fast CI-safe checks."""

from __future__ import annotations

from app.agent import root_agent
from app.specialists import action_agent, memory_agent, pipeline_agent


def test_mission_control_has_guardian_tools():
    names = {t.__name__ for t in root_agent.tools}
    assert "guardian_approve_write" in names
    assert "guardian_deny_write" in names


def test_mission_control_delegates_to_three_specialists():
    subs = {a.name for a in root_agent.sub_agents}
    assert subs == {"memory_agent", "pipeline_agent", "action_agent"}


def test_memory_agent_has_context_pack_tool():
    names = {t.__name__ for t in memory_agent.tools}
    assert "get_team_context" in names
    assert "get_decision_memory" in names
    assert "query_bigquery" in names


def test_pipeline_agent_has_fivetran_tools():
    names = {t.__name__ for t in pipeline_agent.tools}
    assert "fivetran_list_connections" in names
    assert "fivetran_sync_connection" in names


def test_action_agent_has_export_tools():
    names = {t.__name__ for t in action_agent.tools}
    assert "prepare_insight_report" in names
    assert "export_report_to_gcs" in names


def test_all_agents_use_gemini_25_flash():
    for agent in (root_agent, memory_agent, pipeline_agent, action_agent):
        model_name = getattr(getattr(agent, "model", None), "model", None) or str(agent.model)
        assert "2.5-flash" in model_name
