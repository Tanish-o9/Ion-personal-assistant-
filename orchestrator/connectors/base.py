"""
Phase 57: Base Connector Abstract Interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from orchestrator.connectors.models import ConnectorDescriptor, PermissionScope

class BaseConnector(ABC):
    """Abstract base class for all JARVIS service connectors."""

    def __init__(self, descriptor: ConnectorDescriptor):
        self.descriptor = descriptor
        self._authenticated = False

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticates with the external provider without logging sensitive secrets."""
        pass

    @abstractmethod
    def read(self, resource_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reads data from the external provider."""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new record on the external provider (requires approval for HIGH risk)."""
        pass

    @abstractmethod
    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing record on the external provider."""
        pass

    @abstractmethod
    def delete(self, resource_id: str) -> bool:
        """Deletes a record on the external provider."""
        pass

    def health(self) -> Dict[str, Any]:
        """Returns health status of the connector."""
        return {
            "connector_id": self.descriptor.connector_id,
            "status": "HEALTHY" if self._authenticated else "UNAUTHENTICATED",
            "is_enabled": self.descriptor.is_enabled
        }
