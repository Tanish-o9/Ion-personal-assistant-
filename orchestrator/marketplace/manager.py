"""
Phase 61: Capability Marketplace Manager.
"""

from typing import Dict, Any, List, Optional
from orchestrator.marketplace.models import MarketplaceCapabilityEntry, CapabilityCategory

class MarketplaceManager:
    """Manages capability catalog discovery, evaluation security, compatibility, installation, updates, and rollbacks."""

    def __init__(self):
        self._catalog: Dict[str, MarketplaceCapabilityEntry] = {}
        self._installed: Dict[str, MarketplaceCapabilityEntry] = {}
        self._installed_versions: Dict[str, List[str]] = {}  # cap_id -> list of historical versions

        # Seed standard capability templates
        self._seed_default_catalog()

    def _seed_default_catalog(self):
        e1 = MarketplaceCapabilityEntry(
            id="market_jira_connector",
            name="Jira Connector",
            description="Sync issues and tasks with Atlassian Jira",
            publisher="JARVIS Official",
            category=CapabilityCategory.CONNECTOR,
            capabilities=["read_jira", "create_jira_issue"],
            permissions=["READ", "CREATE"],
            risk_level="MEDIUM",
            min_jarvis_version="2.0.0",
            evaluation_score=0.98
        )
        e2 = MarketplaceCapabilityEntry(
            id="market_code_reviewer",
            name="AI Code Reviewer Skill",
            description="Perform security and style reviews on pull requests",
            publisher="Community Contributor",
            category=CapabilityCategory.SKILL,
            capabilities=["code_analysis"],
            permissions=["READ"],
            risk_level="LOW",
            min_jarvis_version="2.0.0",
            evaluation_score=0.92
        )
        self._catalog[e1.id] = e1
        self._catalog[e2.id] = e2

    def discover_capabilities(self, category: Optional[CapabilityCategory] = None, search_query: Optional[str] = None) -> List[MarketplaceCapabilityEntry]:
        items = list(self._catalog.values())
        if category:
            items = [i for i in items if i.category == category]
        if search_query:
            sq = search_query.lower()
            items = [i for i in items if sq in i.name.lower() or sq in i.description.lower()]
        return items

    def evaluate_capability(self, capability_id: str) -> Dict[str, Any]:
        entry = self._catalog.get(capability_id)
        if not entry:
            return {"status": "error", "message": f"Capability '{capability_id}' not found"}

        return {
            "status": "APPROVED" if entry.evaluation_score >= 0.8 else "REVIEW_REQUIRED",
            "capability_id": entry.id,
            "evaluation_score": entry.evaluation_score,
            "risk_level": entry.risk_level,
            "permissions": entry.permissions
        }

    def install_capability(self, capability_id: str, user_id: str) -> Dict[str, Any]:
        entry = self._catalog.get(capability_id)
        if not entry:
            return {"status": "error", "message": f"Capability '{capability_id}' not found"}

        eval_res = self.evaluate_capability(capability_id)
        if eval_res["status"] == "REVIEW_REQUIRED":
            return {"status": "error", "message": "Capability failed security evaluation threshold"}

        entry.is_installed = True
        self._installed[capability_id] = entry
        if capability_id not in self._installed_versions:
            self._installed_versions[capability_id] = []
        self._installed_versions[capability_id].append(entry.version)

        return {"status": "installed", "capability": entry}

    def rollback_capability(self, capability_id: str) -> Dict[str, Any]:
        if capability_id not in self._installed:
            return {"status": "error", "message": f"Capability '{capability_id}' is not installed"}

        versions = self._installed_versions.get(capability_id, [])
        if len(versions) < 2:
            return {"status": "error", "message": "No previous version available for rollback"}

        current_ver = versions.pop()
        prev_ver = versions[-1]
        self._installed[capability_id].version = prev_ver

        return {"status": "rolled_back", "capability_id": capability_id, "previous_version": prev_ver}

default_marketplace_manager = MarketplaceManager()
