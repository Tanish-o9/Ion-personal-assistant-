import pytest
from orchestrator.computer import default_computer_manager, default_computer_allowlist, ComputerActionRequest

def test_computer_allowlist_evaluation():
    # Read screen -> low risk
    risk, req_confirm = default_computer_allowlist.evaluate_action("browser", "github.com", "read_screen")
    assert risk == "low"
    assert req_confirm is False

    # Blocked keyword -> blocked
    risk_bl, _ = default_computer_allowlist.evaluate_action("browser", "password_reset", "click")
    assert risk_bl == "blocked"

def test_computer_interaction_session_and_execution():
    user_id = "user_comp_1"
    sess = default_computer_manager.create_session(user_id=user_id, application="browser", target="github.com")
    assert sess.session_id is not None

    screen = default_computer_manager.inspect_screen(sess.session_id)
    assert screen.application == "browser"
    assert len(screen.detected_controls) >= 1

    req = ComputerActionRequest(
        session_id=sess.session_id,
        application="browser",
        action_type="read_screen",
    )
    res = default_computer_manager.execute_action(req, user_id=user_id)
    assert res.success is True
    assert res.risk_level == "low"
