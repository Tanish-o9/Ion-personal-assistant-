"""
Phase 87: Controlled Smart Environment Engine.
Manages environments, aggregated states, scenes, and safe automation workflows.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestrator.devices.models import DeviceCapability
from orchestrator.devices.registry import default_device_registry
from database.connection import get_db_context
from database.models import EnvironmentModel, SceneModel, utc_now_iso

class EnvironmentDetail(BaseModel):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    name: str
    description: str = ""
    device_ids: List[str] = Field(default_factory=list)
    policies: Dict[str, Any] = Field(default_factory=dict)

class EnvironmentState(BaseModel):
    environment_id: str
    device_states: Dict[str, Any] = Field(default_factory=dict)
    sensor_values: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=utc_now_iso)

class EnvironmentAction(BaseModel):
    device_id: str
    capability: DeviceCapability
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"
    approval_required: bool = False

class SceneDetail(BaseModel):
    id: str
    environment_id: str
    name: str
    actions: List[EnvironmentAction] = Field(default_factory=list)
    is_enabled: bool = True
    version: int = 1

class EnvironmentManager:
    """Manages smart environments, scenes, and aggregated states."""

    def create_environment(
        self,
        user_id: str,
        name: str,
        description: str = "",
        device_ids: Optional[List[str]] = None,
        workspace_id: Optional[str] = None
    ) -> EnvironmentDetail:
        env_id = f"env_{uuid.uuid4().hex[:12]}"
        device_ids = device_ids or []
        dev_ids_json = json.dumps(device_ids)

        with get_db_context() as db:
            em = EnvironmentModel(
                id=env_id,
                user_id=user_id,
                workspace_id=workspace_id,
                name=name,
                description=description,
                device_ids_json=dev_ids_json
            )
            db.add(em)
            db.commit()
            db.refresh(em)
            return self._to_detail(em)

    def get_environment(self, env_id: str, user_id: str) -> Optional[EnvironmentDetail]:
        with get_db_context() as db:
            em = db.query(EnvironmentModel).filter(EnvironmentModel.id == env_id, EnvironmentModel.user_id == user_id).first()
            return self._to_detail(em) if em else None

    def get_environment_state(self, env_id: str, user_id: str) -> EnvironmentState:
        env = self.get_environment(env_id, user_id)
        if not env:
            raise ValueError(f"Environment {env_id} not found or unauthorized")

        device_states = {}
        sensor_values = {}
        for dev_id in env.device_ids:
            try:
                res = default_device_registry.execute_device_action(
                    user_id=user_id,
                    device_id=dev_id,
                    capability=DeviceCapability.READ_STATUS
                )
                device_states[dev_id] = res.get("result", {}).get("state", {})
            except Exception:
                device_states[dev_id] = {"status": "UNREACHABLE"}

        return EnvironmentState(
            environment_id=env_id,
            device_states=device_states,
            sensor_values=sensor_values
        )

    def create_scene(
        self,
        env_id: str,
        user_id: str,
        name: str,
        actions: List[EnvironmentAction]
    ) -> SceneDetail:
        env = self.get_environment(env_id, user_id)
        if not env:
            raise ValueError(f"Environment {env_id} not found or unauthorized")

        scene_id = f"scene_{uuid.uuid4().hex[:12]}"
        actions_json = json.dumps([a.model_dump() for a in actions])

        with get_db_context() as db:
            sm = SceneModel(
                id=scene_id,
                environment_id=env_id,
                name=name,
                actions_json=actions_json,
                is_enabled=True,
                version=1
            )
            db.add(sm)
            db.commit()
            db.refresh(sm)
            return self._to_scene_detail(sm)

    def execute_scene(self, scene_id: str, user_id: str) -> Dict[str, Any]:
        """Executes predefined safe scene actions through risk checks."""
        with get_db_context() as db:
            sm = db.query(SceneModel).filter(SceneModel.id == scene_id).first()
            if not sm:
                raise ValueError(f"Scene {scene_id} not found")
            scene = self._to_scene_detail(sm)

        executed = []
        pending_approvals = []

        for action in scene.actions:
            if action.risk_level == "HIGH":
                action.approval_required = True
                pending_approvals.append(action.model_dump())
                continue

            try:
                res = default_device_registry.execute_device_action(
                    user_id=user_id,
                    device_id=action.device_id,
                    capability=action.capability,
                    parameters=action.parameters
                )
                executed.append(res)
            except Exception as e:
                executed.append({"device_id": action.device_id, "error": str(e)})

        return {
            "scene_id": scene_id,
            "scene_name": scene.name,
            "executed_actions": executed,
            "pending_approvals": pending_approvals,
            "status": "WAITING_FOR_APPROVAL" if pending_approvals else "COMPLETED"
        }

    @staticmethod
    def _to_detail(em: EnvironmentModel) -> EnvironmentDetail:
        dev_ids = json.loads(em.device_ids_json or "[]")
        policies = json.loads(em.policies_json or "{}")
        return EnvironmentDetail(
            id=em.id,
            user_id=em.user_id,
            workspace_id=em.workspace_id,
            name=em.name,
            description=em.description,
            device_ids=dev_ids,
            policies=policies
        )

    @staticmethod
    def _to_scene_detail(sm: SceneModel) -> SceneDetail:
        raw_actions = json.loads(sm.actions_json or "[]")
        actions = [EnvironmentAction(**a) for a in raw_actions]
        return SceneDetail(
            id=sm.id,
            environment_id=sm.environment_id,
            name=sm.name,
            actions=actions,
            is_enabled=sm.is_enabled,
            version=sm.version
        )

default_environment_manager = EnvironmentManager()
