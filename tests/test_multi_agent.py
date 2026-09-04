import pytest
from orchestrator.agents import default_supervisor, AgentDefinition

def test_agent_registration_and_selection():
    agent = default_supervisor.select_agent_for_task("research")
    assert agent.name == "ResearchAgent"

    coding_agent = default_supervisor.select_agent_for_task("coding")
    assert coding_agent.name == "CodingAgent"

@pytest.mark.asyncio
async def test_supervisor_multi_agent_orchestration():
    res = await default_supervisor.orchestrate_multi_agent(
        user_request="Perform research and inspect repository code",
        required_capabilities=["research", "coding"],
    )
    assert len(res["agents_utilized"]) == 2
    assert "ResearchAgent" in res["agents_utilized"]
    assert "CodingAgent" in res["agents_utilized"]
    assert res["overall_confidence"] in {"high", "medium", "low"}
