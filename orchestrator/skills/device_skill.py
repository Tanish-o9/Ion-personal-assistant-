"""
Phase 90: Higher-Level Device Management Skill.
Orchestrates device discovery, status queries, environment scene execution, and verification.
"""

from typing import Dict, Any, List, Optional
from orchestrator.skills.models import Skill
from orchestrator.skills.registry import SkillRegistry
from orchestrator.devices.models import DeviceCapability, DeviceType
from orchestrator.devices.registry import default_device_registry
from orchestrator.devices.environment import default_environment_manager
from orchestrator.devices.security import default_device_security_policy

class DeviceManagementSkill:
    """Higher-level Skill for managing IoT devices, smart environments, and scenes."""

    def __init__(self):
        self.skill_definition = Skill(
            name="device_management",
            description="Discovers, checks status, executes safe actions, and manages smart environments/scenes",
            capabilities=["device_discovery", "device_control", "environment_coordination", "scene_execution"],
            required_tools=["device_list", "device_status", "device_set_state"],
            risk_level="medium",
            version="v1"
        )

    def execute_skill_action(
        self,
        action_name: str,
        user_id: str,
        parameters: Dict[str, Any],
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:

        if action_name == "list_devices":
            devices = default_device_registry.list_devices(user_id=user_id, workspace_id=workspace_id)
            return {"status": "SUCCESS", "devices": [d.model_dump() for d in devices]}

        elif action_name == "execute_device_action":
            device_id = parameters.get("device_id", "")
            cap_str = parameters.get("capability", "READ_STATUS")
            capability = DeviceCapability(cap_str)
            action_params = parameters.get("parameters", {})

            device = default_device_registry.get_device(device_id, user_id)
            if not device:
                return {"status": "FAILED", "error": f"Device {device_id} not found or unauthorized"}

            # Security Authorization & Audit Check
            auth, risk, req_app, app_id = default_device_security_policy.authorize_and_audit(
                user_id=user_id,
                device=device,
                capability=capability,
                parameters=action_params,
                workspace_id=workspace_id
            )

            if not auth:
                if req_app:
                    return {
                        "status": "WAITING_FOR_APPROVAL",
                        "device_id": device_id,
                        "risk_level": risk,
                        "approval_id": app_id,
                        "message": "High-risk action requires human approval."
                    }
                return {"status": "BLOCKED", "error": f"Action blocked by device security policy: {risk}"}

            res = default_device_registry.execute_device_action(
                user_id=user_id,
                device_id=device_id,
                capability=capability,
                parameters=action_params
            )
            return {"status": "SUCCESS", "result": res}

        elif action_name == "execute_scene":
            scene_id = parameters.get("scene_id", "")
            res = default_environment_manager.execute_scene(scene_id, user_id)
            return {"status": "SUCCESS", "scene_result": res}

        return {"status": "FAILED", "error": f"Unknown skill action '{action_name}'"}

default_device_management_skill = DeviceManagementSkill()
