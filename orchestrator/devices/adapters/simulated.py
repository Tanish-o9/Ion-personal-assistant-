"""
Phase 86: Simulated Device Adapter implementation for development and safe testing.
"""

from typing import Dict, Any, List
from orchestrator.devices.adapters.base import BaseDeviceAdapter
from orchestrator.devices.models import DeviceCapability, DeviceStatus

class SimulatedDeviceAdapter(BaseDeviceAdapter):
    """Simulated device adapter implementing BaseDeviceAdapter."""

    def __init__(self, device_id: str, device_name: str, capabilities: List[DeviceCapability]):
        self.device_id = device_id
        self.device_name = device_name
        self.capabilities = capabilities
        self.is_connected = False
        self.state: Dict[str, Any] = {"power": "OFF", "brightness": 100, "temperature": 22.0, "display_text": ""}

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def get_device_info(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "provider": "simulated",
            "connected": self.is_connected
        }

    def get_status(self) -> DeviceStatus:
        return DeviceStatus.ONLINE if self.is_connected else DeviceStatus.OFFLINE

    def list_capabilities(self) -> List[DeviceCapability]:
        return self.capabilities

    def execute_action(self, capability: DeviceCapability, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if capability not in self.capabilities:
            raise ValueError(f"Capability {capability.value} not supported by device {self.device_id}")

        if capability == DeviceCapability.READ_STATUS or capability == DeviceCapability.READ_SENSOR:
            return {"status": "SUCCESS", "state": dict(self.state)}

        if capability == DeviceCapability.SET_STATE:
            power = parameters.get("power", "ON")
            self.state["power"] = power
            return {"status": "SUCCESS", "updated_state": dict(self.state)}

        if capability == DeviceCapability.SET_BRIGHTNESS:
            val = float(parameters.get("brightness", 100))
            self.state["brightness"] = max(0, min(100, val))
            return {"status": "SUCCESS", "updated_state": dict(self.state)}

        if capability == DeviceCapability.SET_TEMPERATURE:
            temp = float(parameters.get("temperature", 22.0))
            self.state["temperature"] = temp
            return {"status": "SUCCESS", "updated_state": dict(self.state)}

        if capability == DeviceCapability.DISPLAY_MESSAGE:
            msg = str(parameters.get("message", ""))
            self.state["display_text"] = msg
            return {"status": "SUCCESS", "updated_state": dict(self.state)}

        return {"status": "SUCCESS", "action": capability.value, "state": dict(self.state)}
