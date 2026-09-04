"""
Phase 86: Device Integration Layer Tests.
"""

import pytest
from orchestrator.devices.models import DeviceType, DeviceCapability, DeviceStatus
from orchestrator.devices.registry import DeviceRegistry, default_device_registry
from database.connection import get_db_context
from database.models import UserModel

@pytest.fixture(autouse=True)
def setup_test_user():
    with get_db_context() as db:
        user = db.query(UserModel).filter_by(id="test_dev_user").first()
        if not user:
            user = UserModel(id="test_dev_user", username="dev_user", password_hash="hash")
            db.add(user)
            db.commit()

def test_device_registration_and_lookup():
    dev = default_device_registry.register_device(
        user_id="test_dev_user",
        name="Office Smart Light",
        device_type=DeviceType.LIGHT,
        capabilities=[DeviceCapability.READ_STATUS, DeviceCapability.SET_STATE, DeviceCapability.SET_BRIGHTNESS]
    )

    assert dev.id.startswith("dev_")
    assert dev.name == "Office Smart Light"
    assert dev.type == DeviceType.LIGHT
    assert len(dev.capabilities) == 3

    fetched = default_device_registry.get_device(dev.id, user_id="test_dev_user")
    assert fetched is not None
    assert fetched.name == "Office Smart Light"

def test_tenant_isolation_and_filtering():
    dev = default_device_registry.register_device(
        user_id="test_dev_user",
        name="Living Room Display",
        device_type=DeviceType.DISPLAY,
        capabilities=[DeviceCapability.DISPLAY_MESSAGE]
    )

    user_devices = default_device_registry.list_devices(user_id="test_dev_user")
    assert len(user_devices) >= 1

    # Other user isolation check
    other_devices = default_device_registry.list_devices(user_id="unauthorized_user")
    assert len(other_devices) == 0


def test_simulated_adapter_action_execution():
    dev = default_device_registry.register_device(
        user_id="test_dev_user",
        name="Smart Thermostat",
        device_type=DeviceType.THERMOSTAT,
        capabilities=[DeviceCapability.READ_STATUS, DeviceCapability.SET_TEMPERATURE]
    )

    res = default_device_registry.execute_device_action(
        user_id="test_dev_user",
        device_id=dev.id,
        capability=DeviceCapability.SET_TEMPERATURE,
        parameters={"temperature": 24.5}
    )

    assert res["capability"] == "SET_TEMPERATURE"
    assert res["result"]["status"] == "SUCCESS"
    assert res["result"]["updated_state"]["temperature"] == 24.5

def test_unsupported_capability_rejection():
    dev = default_device_registry.register_device(
        user_id="test_dev_user",
        name="Simple Plug",
        device_type=DeviceType.SMART_PLUG,
        capabilities=[DeviceCapability.SET_STATE]
    )

    with pytest.raises(ValueError, match="not supported"):
        default_device_registry.execute_device_action(
            user_id="test_dev_user",
            device_id=dev.id,
            capability=DeviceCapability.DISPLAY_MESSAGE,
            parameters={"message": "Hello"}
        )
