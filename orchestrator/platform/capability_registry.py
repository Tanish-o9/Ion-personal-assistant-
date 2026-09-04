from typing import Any, Dict, List, Optional

from orchestrator.tools import default_registry as tool_registry
from orchestrator.skills import default_skill_registry as skill_registry
from orchestrator.agents import default_supervisor as supervisor
from orchestrator.plugins import default_plugin_registry as plugin_registry

class UnifiedCapabilityRegistry:
    """
    Unified capability discovery layer aggregating Tools, Skills, Sub-Agents, and Plugins
    into a single discovery interface.
    """
    def search_capabilities(self, query: str) -> Dict[str, List[Any]]:
        q_lower = query.lower().strip()

        matching_tools = [
            t.get("name", "") for t in tool_registry.list_tools()
            if isinstance(t, dict) and (q_lower in t.get("name", "").lower() or q_lower in t.get("description", "").lower())
        ]

        raw_skills = skill_registry.list_skills()
        matching_skills = []
        for s in raw_skills:
            if isinstance(s, dict):
                if q_lower in s.get("name", "").lower() or q_lower in s.get("description", "").lower():
                    matching_skills.append(s.get("name", ""))
            elif hasattr(s, "name"):
                if q_lower in getattr(s, "name", "").lower() or q_lower in getattr(s, "description", "").lower():
                    matching_skills.append(getattr(s, "name", ""))

        matching_agents = [
            a.name for a in supervisor.agents.values()
            if q_lower in a.name.lower() or any(q_lower in cap for cap in a.capabilities)
        ]

        matching_plugins = [
            p.manifest.name for p in plugin_registry.search_capabilities(q_lower)
        ]

        return {
            "tools": matching_tools,
            "skills": matching_skills,
            "agents": matching_agents,
            "plugins": matching_plugins,
        }

default_capability_registry = UnifiedCapabilityRegistry()
