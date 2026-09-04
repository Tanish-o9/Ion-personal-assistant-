"""
Phase 54: Offline Capability Manager & Local Gateway Routing.
"""

from typing import Dict, Any, List, Optional
from orchestrator.offline.models import CapabilityDescriptor, NetworkStatus, PrivacyMode
from orchestrator.offline.sync import OfflineSyncManager

class EdgeOfflineManager:
    """Provides capability matrix, privacy mode routing, and offline state awareness."""
    DEFAULT_CAPABILITIES = {
        "text_summarization": CapabilityDescriptor(name="text_summarization", available_online=True, available_offline=True, requires_local_model=True),
        "local_file_reading": CapabilityDescriptor(name="local_file_reading", available_online=True, available_offline=True),
        "cloud_web_research": CapabilityDescriptor(name="cloud_web_research", available_online=True, available_offline=False, requires_cloud=True),
        "cloud_llm_generation": CapabilityDescriptor(name="cloud_llm_generation", available_online=True, available_offline=False, requires_cloud=True),
        "workspace_remote_sync": CapabilityDescriptor(name="workspace_remote_sync", available_online=True, available_offline=False, requires_cloud=True),
    }

    def __init__(self):
        self.network_status = NetworkStatus.ONLINE
        self.privacy_mode = PrivacyMode.ONLINE_ONLY
        self.sync_manager = OfflineSyncManager()

    def set_network_status(self, status: NetworkStatus):
        self.network_status = status

    def set_privacy_mode(self, mode: PrivacyMode):
        self.privacy_mode = mode

    def is_capability_available(self, capability_name: str) -> bool:
        cap = self.DEFAULT_CAPABILITIES.get(capability_name)
        if not cap:
            return False

        if self.network_status == NetworkStatus.OFFLINE:
            return cap.available_offline

        if self.privacy_mode == PrivacyMode.LOCAL_ONLY and cap.requires_cloud:
            return False

        return True

    def resolve_provider_route(self, is_cloud_available: bool = True) -> str:
        """Determines provider routing (cloud_provider vs local_provider vs fallback)."""
        if self.privacy_mode == PrivacyMode.LOCAL_ONLY:
            return "local_provider"

        if not is_cloud_available or self.network_status == NetworkStatus.OFFLINE:
            return "local_provider" if self.is_capability_available("text_summarization") else "offline_fallback"

        if self.privacy_mode == PrivacyMode.LOCAL_PREFERRED:
            return "local_provider"

        return "cloud_provider"

default_edge_offline_manager = EdgeOfflineManager()
