from typing import Any, Dict, List, Optional
from orchestrator.personalization.models import PersonalizationSettings, ProjectContext
from orchestrator.cache import default_cache, make_cache_key

class PersonalizationManager:
    """
    Manages user response preferences, detail levels, project context matching,
    and hierarchy-aware prompt shaping.
    """
    def __init__(self):
        self._user_settings: Dict[str, PersonalizationSettings] = {}
        self._user_projects: Dict[str, List[ProjectContext]] = {}

    def get_settings(self, user_id: str) -> PersonalizationSettings:
        if user_id not in self._user_settings:
            cache_key = make_cache_key("person_settings", user_id)
            cached = default_cache.get(cache_key)
            if cached:
                self._user_settings[user_id] = PersonalizationSettings(**cached)
            else:
                self._user_settings[user_id] = PersonalizationSettings(user_id=user_id)
        return self._user_settings[user_id]

    def update_settings(self, user_id: str, updates: Dict[str, Any]) -> PersonalizationSettings:
        settings = self.get_settings(user_id)
        for key, val in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, val)

        self._user_settings[user_id] = settings
        cache_key = make_cache_key("person_settings", user_id)
        default_cache.set(cache_key, settings.to_dict(), ttl_seconds=3600)
        return settings

    def add_project(self, project: ProjectContext) -> None:
        if project.user_id not in self._user_projects:
            self._user_projects[project.user_id] = []
        self._user_projects[project.user_id].append(project)

    def find_active_project(self, user_id: str, text: str) -> Optional[ProjectContext]:
        if not text or user_id not in self._user_projects:
            return None

        text_lower = text.lower()
        for proj in self._user_projects[user_id]:
            if proj.name.lower() in text_lower:
                return proj
        return None

    def build_personalized_instructions(
        self,
        user_id: str,
        active_project: Optional[ProjectContext] = None,
    ) -> str:
        settings = self.get_settings(user_id)
        if not settings.personalization_enabled:
            return ""

        parts = [
            f"User Communication Preferences:\n- Preferred Style: {settings.response_style}\n- Preferred Language: {settings.preferred_language}\n- Detail Level: {settings.preferred_detail_level}"
        ]

        if active_project:
            parts.append(
                f"\nActive Project Context:\n- Project Name: {active_project.name}\n- Description: {active_project.description}"
            )

        parts.append(
            "\nNote: Current explicit user instructions in the query ALWAYS override stored preferences."
        )

        return "\n".join(parts)

default_personalization_manager = PersonalizationManager()
