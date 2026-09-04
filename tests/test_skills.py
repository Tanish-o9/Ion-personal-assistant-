import pytest
from orchestrator.skills import Skill, SkillRegistry, default_skill_registry

def test_skill_registry_registration_and_lookup():
    reg = SkillRegistry()
    skill = Skill(
        name="custom_skill",
        description="A custom workflow skill",
        capabilities=["custom", "workflow"],
        required_tools=["calculator"],
    )
    reg.register(skill)

    found = reg.get("custom_skill")
    assert found is not None
    assert found.name == "custom_skill"
    assert "custom" in found.capabilities

def test_skill_capability_search_and_toggle():
    reg = default_skill_registry
    results = reg.search_by_capability("research")
    assert len(results) >= 1
    assert results[0].name == "research_skill"

    # Disable skill
    reg.disable_skill("research_skill")
    results_after_disable = reg.search_by_capability("research")
    assert len(results_after_disable) == 0

    # Re-enable skill
    reg.enable_skill("research_skill")
    results_after_enable = reg.search_by_capability("research")
    assert len(results_after_enable) >= 1

def test_builtin_skills_presence():
    skills = default_skill_registry.list_skills()
    names = {s["name"] for s in skills}
    assert "research_skill" in names
    assert "knowledge_skill" in names
    assert "document_analysis_skill" in names
    assert "coding_assistance_skill" in names
