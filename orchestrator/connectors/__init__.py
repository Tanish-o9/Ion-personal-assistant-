"""
Phase 57: Connectors Module.
"""

from orchestrator.connectors.models import PermissionScope, ConnectorDescriptor
from orchestrator.connectors.base import BaseConnector
from orchestrator.connectors.registry import ConnectorRegistry, default_connector_registry
from orchestrator.connectors.platform import UniversalConnectorSDK, default_universal_connector_sdk

__all__ = [
    "PermissionScope",
    "ConnectorDescriptor",
    "BaseConnector",
    "ConnectorRegistry",
    "default_connector_registry",
    "UniversalConnectorSDK",
    "default_universal_connector_sdk",
]

