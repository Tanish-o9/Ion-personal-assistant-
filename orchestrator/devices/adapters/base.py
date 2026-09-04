"""
Phase 86: Generic Device Adapter Abstract Class.
All provider-specific implementations sit cleanly behind this abstraction.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from orchestrator.devices.models import DeviceCapability, DeviceStatus

class BaseDeviceAdapter(ABC):
    """Generic interface for device integration adapters."""

    @abstractmethod
    def connect(self) -> bool:
        """Establishes connection to provider API or device."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Safely disconnects adapter from provider API."""
        pass

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """Returns provider device metadata."""
        pass

    @abstractmethod
    def get_status(self) -> DeviceStatus:
        """Returns current operational status."""
        pass

    @abstractmethod
    def list_capabilities(self) -> List[DeviceCapability]:
        """Lists supported capabilities."""
        pass

    @abstractmethod
    def execute_action(self, capability: DeviceCapability, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a safe device action."""
        pass
