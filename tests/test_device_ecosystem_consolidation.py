"""
Phase 90: Device Ecosystem Consolidation Tests.
"""

import pytest
from orchestrator.devices.models import DeviceType, DeviceCapability
from orchestrator.devices.registry import default_device_registry
from orchestrator.skills.device_skill import default_device_management_skill
from database.connection import get_db_context
from database.models import UserModel

@pytest.fixture(autouse=True)
def setup_test_user():
    with get_db_context() as db:
        user = db.query(UserModel).filter_by(id="test_eco_user").first()
        if not user:
            user = UserModel(id="test_eco_user", username="eco_user", password_hash="hash")
            db.add(user)
            db.commit()

def test_device_skill_list_and_control():
    dev = default_device_registry.register_device(
        user_id="test_eco_user",
        name="Laboratory Display",
        device_type=DeviceType.DISPLAY,
        capabilities=[DeviceCapability.READ_STATUS, DeviceCapability.DISPLAY_MESSAGE]
    )

    # Test list_devices via Skill
    res_list = default_device_management_skill.execute_skill_action(
        action_name="list_devices",
        user_id="test_eco_user",
        parameters={}
    )
    assert res_list["status"] == "SUCCESS"
    assert len(res_list["devices"]) >= 1

    # Test execute_device_action via Skill
    res_ctrl = default_device_management_skill.execute_skill_action(
        action_name="execute_device_action",
        user_id="test_eco_user",
        parameters={
            "device_id": dev.id,
            "capability": "DISPLAY_MESSAGE",
            "parameters": {"message": "Experiment Completed"}
        }
    )
    assert res_ctrl["status"] == "SUCCESS"
    assert res_ctrl["result"]["result"]["status"] == "SUCCESS"
    assert res_ctrl["result"]["result"]["updated_state"]["display_text"] == "Experiment Completed"
