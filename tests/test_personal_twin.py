"""
Unit Tests for Phase 67: Personal AI Twin / Working-Style Model.
"""

import pytest
from orchestrator.personalization import PersonalTwinManager

def test_working_style_creation_and_precedence():
    tm = PersonalTwinManager()
    user_id = "user_twin_1"

    # Update working style
    tm.update_working_style(user_id, {"response_preferences": "step_by_step", "technical_level": "intermediate"})
    twin = tm.get_or_create_twin(user_id)
    assert twin.response_preferences == "step_by_step"
    assert twin.technical_level == "intermediate"

    # Resolve effective preference -> Stored
    res_stored = tm.resolve_effective_preference(user_id)
    assert res_stored["source"] == "stored_twin_preference"
    assert res_stored["response_style"] == "step_by_step"

    # Precedence 1: Current instruction override
    res_curr = tm.resolve_effective_preference(user_id, current_instruction_override="concise")
    assert res_curr["source"] == "current_instruction"
    assert res_curr["response_style"] == "concise"

    # Precedence 2: Project preference
    res_proj = tm.resolve_effective_preference(user_id, project_preference="detailed")
    assert res_proj["source"] == "project_preference"
    assert res_proj["response_style"] == "detailed"

def test_personalization_toggle():
    tm = PersonalTwinManager()
    user_id = "user_twin_2"

    tm.disable_personalization(user_id)
    res = tm.resolve_effective_preference(user_id)
    assert res["source"] == "personalization_disabled"
    assert res["response_style"] == "default"
