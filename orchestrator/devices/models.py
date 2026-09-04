"""
Phase 86: Device Integration Models & Enums.
"""

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DeviceType(str, enum.Enum):
    LIGHT = "LIGHT"
    THERMOSTAT = "THERMOSTAT"
    DISPLAY = "DISPLAY"
    SPEAKER = "SPEAKER"
    SENSOR = "SENSOR"
    SMART_PLUG = "SMART_PLUG"
    CAMERA_STATUS_ONLY = "CAMERA_STATUS_ONLY"
    OTHER = "OTHER"

class DeviceCapability(str, enum.Enum):
    READ_STATUS = "READ_STATUS"
    READ_SENSOR = "READ_SENSOR"
    SET_STATE = "SET_STATE"
    SET_BRIGHTNESS = "SET_BRIGHTNESS"
    SET_TEMPERATURE = "SET_TEMPERATURE"
    PLAY_MEDIA = "PLAY_MEDIA"
    DISPLAY_MESSAGE = "DISPLAY_MESSAGE"

class DeviceStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    DISABLED = "DISABLED"

class DeviceDetail(BaseModel):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    name: str
    type: DeviceType = DeviceType.OTHER
    provider: str = "simulated"
    capabilities: List[DeviceCapability] = Field(default_factory=list)
    status: DeviceStatus = DeviceStatus.ONLINE
    metadata: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    is_enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DeviceActionPayload(BaseModel):
    device_id: str
    capability: DeviceCapability
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"
