import logging
from typing import Any, Dict, List, Optional
from orchestrator.skills.models import Skill

logger = logging.getLogger(__name__)

class SkillRegistry:
    """
    Registry for managing and discovering higher-level agent Skills.
    """
    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if not skill.name:
            raise ValueError("Skill name cannot be empty.")
        self._skills[skill.name] = skill
        logger.info("Registered skill '%s' (v%s)", skill.name, skill.version)

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_skills(self) -> List[Dict[str, Any]]:
        return [skill.to_dict() for skill in self._skills.values()]

    def search_by_capability(self, capability: str) -> List[Skill]:
        cap_lower = capability.lower().strip()
        matched = []
        for skill in self._skills.values():
            if not skill.enabled:
                continue
            if any(cap_lower in c.lower() for c in skill.capabilities):
                matched.append(skill)
        return matched

    def enable_skill(self, name: str) -> bool:
        if name in self._skills:
            self._skills[name].enabled = True
            return True
        return False

    def disable_skill(self, name: str) -> bool:
        if name in self._skills:
            self._skills[name].enabled = False
            return True
        return False
