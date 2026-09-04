import pytest
from orchestrator.personalization import (
    PersonalizationManager,
    PersonalizationSettings,
    ProjectContext,
    default_personalization_manager,
)

def test_personalization_settings_update():
    mgr = PersonalizationManager()
    user_id = "user_pers_1"

    settings = mgr.get_settings(user_id)
    assert settings.response_style == "detailed"

    updated = mgr.update_settings(user_id, {"response_style": "concise", "preferred_language": "Hinglish"})
    assert updated.response_style == "concise"
    assert updated.preferred_language == "Hinglish"

def test_project_context_matching():
    mgr = PersonalizationManager()
    user_id = "user_proj_1"

    project = ProjectContext(
        project_id="p1",
        user_id=user_id,
        name="Project Jarvis",
        description="AI Assistant Platform",
    )
    mgr.add_project(project)

    active = mgr.find_active_project(user_id, "How is Project Jarvis progressing?")
    assert active is not None
    assert active.name == "Project Jarvis"

def test_personalization_instructions_builder():
    mgr = PersonalizationManager()
    user_id = "user_instr_1"
    mgr.update_settings(user_id, {"response_style": "technical"})

    instructions = mgr.build_personalized_instructions(user_id)
    assert "User Communication Preferences" in instructions
    assert "technical" in instructions
    assert "Current explicit user instructions in the query ALWAYS override" in instructions
