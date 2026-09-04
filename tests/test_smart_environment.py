"""
Phase 87: Controlled Smart Environment Tests.
"""

import pytest
from orchestrator.devices.models import DeviceType, DeviceCapability
from orchestrator.devices.registry import default_device_registry
from orchestrator.devices.environment import (
    EnvironmentAction,
    EnvironmentManager,
    default_environment_manager
)
from database.connection import get_db_context
from database.models import UserModel

@pytest.fixture(autouse=True)
def setup_test_user():
    with get_db_context() as db:
        user = db.query(UserModel).filter_by(id="test_env_user").first()
        if not user:
            user = UserModel(id="test_env_user", username="env_user", password_hash="hash")
            db.add(user)
            db.commit()

def test_environment_creation_and_aggregated_state():
    d1 = default_device_registry.register_device(
        user_id="test_env_user",
        name="Office Lamp",
        device_type=DeviceType.LIGHT,
        capabilities=[DeviceCapability.READ_STATUS, DeviceCapability.SET_STATE]
    )

    env = default_environment_manager.create_environment(
        user_id="test_env_user",
        name="Executive Office",
        description="Main workspace environment",
        device_ids=[d1.id]
    )

    assert env.id.startswith("env_")
    assert env.name == "Executive Office"
    assert len(env.device_ids) == 1

    state = default_environment_manager.get_environment_state(env.id, user_id="test_env_user")
    assert state.environment_id == env.id
    assert d1.id in state.device_states

def test_scene_creation_and_execution():
    d1 = default_device_registry.register_device(
        user_id="test_env_user",
        name="Conference Light",
        device_type=DeviceType.LIGHT,
        capabilities=[DeviceCapability.SET_STATE]
    )

    env = default_environment_manager.create_environment(
        user_id="test_env_user",
        name="Conference Room",
        device_ids=[d1.id]
    )

    action1 = EnvironmentAction(
        device_id=d1.id,
        capability=DeviceCapability.SET_STATE,
        parameters={"power": "ON"},
        risk_level="LOW"
    )

    scene = default_environment_manager.create_scene(
        env_id=env.id,
        user_id="test_env_user",
        name="Presentation Mode",
        actions=[action1]
    )

    res = default_environment_manager.execute_scene(scene.id, user_id="test_env_user")
    assert res["status"] == "COMPLETED"
    assert len(res["executed_actions"]) == 1
    assert res["executed_actions"][0]["result"]["status"] == "SUCCESS"


def test_high_risk_scene_action_triggers_approval():
    d1 = default_device_registry.register_device(
        user_id="test_env_user",
        name="Main Power Switch",
        device_type=DeviceType.SMART_PLUG,
        capabilities=[DeviceCapability.SET_STATE]
    )

    env = default_environment_manager.create_environment(
        user_id="test_env_user",
        name="Server Closet",
        device_ids=[d1.id]
    )

    high_risk_action = EnvironmentAction(
        device_id=d1.id,
        capability=DeviceCapability.SET_STATE,
        parameters={"power": "OFF"},
        risk_level="HIGH"
    )

    scene = default_environment_manager.create_scene(
        env_id=env.id,
        user_id="test_env_user",
        name="Emergency Shutdown",
        actions=[high_risk_action]
    )

    res = default_environment_manager.execute_scene(scene.id, user_id="test_env_user")
    assert res["status"] == "WAITING_FOR_APPROVAL"
    assert len(res["pending_approvals"]) == 1
    assert res["pending_approvals"][0]["device_id"] == d1.id
