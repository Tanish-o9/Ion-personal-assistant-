import pytest
from orchestrator.personalization import (
    PersonalizationManager,
    PersonalizationSettings,
    ProjectContext,
)

def test_extended_personalization_settings():
    mgr = PersonalizationManager()
    settings = mgr.update_settings("u_pers_1", {
        "technical_level": "expert",
        "preferred_coding_style": "clean",
        "research_depth": "thorough",
    })

    assert settings.technical_level == "expert"
    assert settings.preferred_coding_style == "clean"
    assert settings.research_depth == "thorough"

def test_project_specific_preferences():
    mgr = PersonalizationManager()
    proj = ProjectContext(
        project_id="p1",
        user_id="u_pers_2",
        name="Backend Core",
        description="Core FastAPI service",
        coding_conventions="PEP8",
        preferred_framework="FastAPI",
    )
    mgr.add_project(proj)

    found = mgr.find_active_project("u_pers_2", "working on Backend Core service")
    assert found is not None
    assert found.coding_conventions == "PEP8"
    assert found.preferred_framework == "FastAPI"

def test_instruction_precedence_in_prompt_building():
    mgr = PersonalizationManager()
    prompt = mgr.build_personalized_instructions("u_pers_3")
    assert "Current explicit user instructions in the query ALWAYS override stored preferences" in prompt
