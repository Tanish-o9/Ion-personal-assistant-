"""
Phase 67: Personal AI Twin & Working-Style Personalization Model.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestrator.personalization.manager import default_personalization_manager

class WorkingStyleModel(BaseModel):
    """User working style and explicitly authorized formatting/communication preferences."""
    user_id: str
    response_preferences: str = "concise" # concise, detailed, step_by_step
    communication_style: str = "professional" # professional, casual, technical
    technical_level: str = "expert" # beginner, intermediate, expert
    preferred_language: str = "en"
    formatting_preferences: List[str] = Field(default_factory=lambda: ["markdown", "code_blocks"])
    coding_preferences: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.9
    is_personalization_enabled: bool = True

class PersonalTwinManager:
    """Manages working style personalization, precedence enforcement, and user control APIs."""

    def __init__(self):
        self._profiles: Dict[str, WorkingStyleModel] = {}

    def get_or_create_twin(self, user_id: str) -> WorkingStyleModel:
        if user_id not in self._profiles:
            self._profiles[user_id] = WorkingStyleModel(user_id=user_id)
        return self._profiles[user_id]

    def update_working_style(self, user_id: str, updates: Dict[str, Any]) -> WorkingStyleModel:
        twin = self.get_or_create_twin(user_id)
        for key, val in updates.items():
            if hasattr(twin, key):
                setattr(twin, key, val)
        return twin

    def resolve_effective_preference(
        self,
        user_id: str,
        current_instruction_override: Optional[str] = None,
        project_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Applies strict precedence rules:
        Current User Instruction > Current Request > Project Preference > Stored Preference > Historical Learning > Default
        """
        twin = self.get_or_create_twin(user_id)
        if not twin.is_personalization_enabled:
            return {"response_style": "default", "source": "personalization_disabled"}

        # 1. Current Instruction Override takes top precedence
        if current_instruction_override:
            return {"response_style": current_instruction_override, "source": "current_instruction"}

        # 2. Project Preference
        if project_preference:
            return {"response_style": project_preference, "source": "project_preference"}

        # 3. Stored Preference
        return {
            "response_style": twin.response_preferences,
            "technical_level": twin.technical_level,
            "formatting": twin.formatting_preferences,
            "source": "stored_twin_preference"
        }

    def disable_personalization(self, user_id: str):
        twin = self.get_or_create_twin(user_id)
        twin.is_personalization_enabled = False

    def enable_personalization(self, user_id: str):
        twin = self.get_or_create_twin(user_id)
        twin.is_personalization_enabled = True

default_personal_twin_manager = PersonalTwinManager()
