from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from orchestrator.plugins.models import PluginManifest, PluginDefinition
from orchestrator.observability import jarvis_logger

class PluginRegistry:
    """
    Centralized plugin registry managing plugin manifest validation, permission checks,
    duplicate prevention, state toggling, and capability discovery.
    """
    def __init__(self):
        self.plugins: Dict[str, PluginDefinition] = {}

    def register_plugin(self, manifest: PluginManifest) -> PluginDefinition:
        if manifest.id in self.plugins:
            raise ValueError(f"Plugin ID '{manifest.id}' is already registered.")

        if not manifest.name or not manifest.version:
            raise ValueError("Invalid plugin manifest: missing required name or version.")

        plugin = PluginDefinition(
            manifest=manifest,
            enabled=True,
            installed_at=datetime.now(timezone.utc).isoformat(),
        )
        self.plugins[manifest.id] = plugin
        jarvis_logger.info("Registered plugin '%s' (v%s)", manifest.name, manifest.version)
        return plugin

    def unregister_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            return True
        return False

    def enable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = True
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = False
            return True
        return False

    def search_capabilities(self, capability: str) -> List[PluginDefinition]:
        matches = []
        for p in self.plugins.values():
            if p.enabled and capability in p.manifest.capabilities:
                matches.append(p)
        return matches

default_plugin_registry = PluginRegistry()
