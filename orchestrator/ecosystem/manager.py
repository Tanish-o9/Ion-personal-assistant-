from typing import Dict, List, Optional
from orchestrator.ecosystem.models import EcosystemCatalogEntry
from orchestrator.ecosystem.pipeline import CapabilityValidationPipeline
from orchestrator.plugins import default_plugin_registry, PluginManifest

class EcosystemManager:
    """
    Central catalog manager for discovering, evaluating, installing, and managing ecosystem capabilities.
    """
    def __init__(self):
        self.catalog: Dict[str, EcosystemCatalogEntry] = {}
        self.installed_user_capabilities: Dict[str, List[str]] = {}

    def submit_capability(self, entry: EcosystemCatalogEntry) -> bool:
        ok, reason = CapabilityValidationPipeline.validate_and_approve(entry)
        if not ok:
            return False
        self.catalog[entry.capability_id] = entry
        return True

    def search_catalog(self, query: str) -> List[EcosystemCatalogEntry]:
        q_lower = query.lower().strip()
        matches = []
        for entry in self.catalog.values():
            if entry.evaluation_status == "passed" and (q_lower in entry.name.lower() or q_lower in entry.description.lower()):
                matches.append(entry)
        return matches

    def install_capability(self, user_id: str, capability_id: str) -> bool:
        entry = self.catalog.get(capability_id)
        if not entry or entry.evaluation_status != "passed":
            return False

        if user_id not in self.installed_user_capabilities:
            self.installed_user_capabilities[user_id] = []

        if capability_id not in self.installed_user_capabilities[user_id]:
            self.installed_user_capabilities[user_id].append(capability_id)

            # Register as plugin if capability_type is plugin
            if entry.capability_type == "plugin":
                try:
                    default_plugin_registry.register_plugin(
                        PluginManifest(
                            id=entry.capability_id,
                            name=entry.name,
                            version=entry.version,
                            description=entry.description,
                            permissions=entry.required_permissions,
                        )
                    )
                except ValueError:
                    pass

        return True

    def uninstall_capability(self, user_id: str, capability_id: str) -> bool:
        if user_id in self.installed_user_capabilities:
            if capability_id in self.installed_user_capabilities[user_id]:
                self.installed_user_capabilities[user_id].remove(capability_id)
                default_plugin_registry.unregister_plugin(capability_id)
                return True
        return False

default_ecosystem_manager = EcosystemManager()
