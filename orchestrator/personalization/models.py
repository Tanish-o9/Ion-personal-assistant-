from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PersonalizationSettings(BaseModel):
    user_id: str
    response_style: str = "detailed"          # concise, detailed, technical
    preferred_language: str = "English"       # English, Hinglish, Spanish, etc.
    preferred_detail_level: str = "normal"    # summary, normal, deep
    formatting_preferences: str = "markdown"  # markdown, plain_text, code_blocks
    technical_level: str = "expert"           # beginner, intermediate, expert
    preferred_coding_style: str = "clean"      # clean, verbose, concise
    research_depth: str = "thorough"          # quick, thorough
    personalization_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "response_style": self.response_style,
            "preferred_language": self.preferred_language,
            "preferred_detail_level": self.preferred_detail_level,
            "formatting_preferences": self.formatting_preferences,
            "technical_level": self.technical_level,
            "preferred_coding_style": self.preferred_coding_style,
            "research_depth": self.research_depth,
            "personalization_enabled": self.personalization_enabled,
        }

class ProjectContext(BaseModel):
    project_id: str
    user_id: str
    name: str
    description: str
    goals: List[str] = Field(default_factory=list)
    knowledge_scope: str = "project"
    active_tasks: List[str] = Field(default_factory=list)
    coding_conventions: Optional[str] = None
    preferred_framework: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "goals": self.goals,
            "knowledge_scope": self.knowledge_scope,
            "active_tasks": self.active_tasks,
            "coding_conventions": self.coding_conventions,
            "preferred_framework": self.preferred_framework,
        }
