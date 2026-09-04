"""
FastAPI Router for JARVIS 4.3 (Phases 86–90: IoT, Device Integration, Smart Environment, Edge Intelligence).
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from orchestrator.devices.models import DeviceType, DeviceCapability, DeviceActionPayload
from orchestrator.devices.registry import default_device_registry
from orchestrator.devices.environment import default_environment_manager, EnvironmentAction
from orchestrator.devices.security import default_device_security_policy
from orchestrator.skills.device_skill import default_device_management_skill
from orchestrator.platform.edge import default_edge_runtime, PrivacyMode

router = APIRouter(prefix="/api/v1", tags=["JARVIS 4.3 Devices & Edge"])

class DeviceRegisterPayload(BaseModel):
    name: str
    device_type: str = "OTHER"
    provider: str = "simulated"
    capabilities: List[str] = ["READ_STATUS", "SET_STATE"]
    workspace_id: Optional[str] = None

class EnvironmentCreatePayload(BaseModel):
    name: str
    description: str = ""
    device_ids: List[str] = []
    workspace_id: Optional[str] = None

class SceneCreatePayload(BaseModel):
    name: str
    actions: List[Dict[str, Any]]


@router.get("/devices")
def list_devices(user_id: str = "default_user", workspace_id: Optional[str] = None):
    devices = default_device_registry.list_devices(user_id=user_id, workspace_id=workspace_id)
    return {"devices": [d.model_dump() for d in devices]}


@router.post("/devices")
def register_device(payload: DeviceRegisterPayload, user_id: str = "default_user"):
    caps = [DeviceCapability(c) for c in payload.capabilities]
    dtype = DeviceType(payload.device_type)
    dev = default_device_registry.register_device(
        user_id=user_id,
        name=payload.name,
        device_type=dtype,
        provider=payload.provider,
        capabilities=caps,
        workspace_id=payload.workspace_id
    )
    return dev.model_dump()


@router.get("/devices/{device_id}")
def get_device(device_id: str, user_id: str = "default_user"):
    dev = default_device_registry.get_device(device_id, user_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return dev.model_dump()


@router.get("/devices/{device_id}/status")
def get_device_status(device_id: str, user_id: str = "default_user"):
    res = default_device_management_skill.execute_skill_action(
        action_name="execute_device_action",
        user_id=user_id,
        parameters={"device_id": device_id, "capability": "READ_STATUS"}
    )
    return res


@router.get("/devices/{device_id}/capabilities")
def get_device_capabilities(device_id: str, user_id: str = "default_user"):
    dev = default_device_registry.get_device(device_id, user_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"device_id": device_id, "capabilities": [c.value for c in dev.capabilities]}


@router.post("/devices/{device_id}/actions")
def execute_device_action(device_id: str, payload: DeviceActionPayload, user_id: str = "default_user"):
    res = default_device_management_skill.execute_skill_action(
        action_name="execute_device_action",
        user_id=user_id,
        parameters={
            "device_id": device_id,
            "capability": payload.capability.value,
            "parameters": payload.parameters
        }
    )
    return res


@router.get("/environments")
def get_environments(user_id: str = "default_user"):
    # Return sample environment list
    return {"environments": []}


@router.post("/environments")
def create_environment(payload: EnvironmentCreatePayload, user_id: str = "default_user"):
    env = default_environment_manager.create_environment(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        device_ids=payload.device_ids,
        workspace_id=payload.workspace_id
    )
    return env.model_dump()


@router.get("/environments/{env_id}")
def get_environment(env_id: str, user_id: str = "default_user"):
    env = default_environment_manager.get_environment(env_id, user_id)
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    state = default_environment_manager.get_environment_state(env_id, user_id)
    return {"environment": env.model_dump(), "state": state.model_dump()}


@router.post("/environments/{env_id}/scenes")
def create_scene(env_id: str, payload: SceneCreatePayload, user_id: str = "default_user"):
    actions = [EnvironmentAction(**a) for a in payload.actions]
    scene = default_environment_manager.create_scene(env_id=env_id, user_id=user_id, name=payload.name, actions=actions)
    return scene.model_dump()


@router.post("/scenes/{scene_id}/execute")
def execute_scene(scene_id: str, user_id: str = "default_user"):
    res = default_environment_manager.execute_scene(scene_id, user_id)
    return res


@router.get("/edge/status")
def get_edge_status():
    return default_edge_runtime.get_health()
