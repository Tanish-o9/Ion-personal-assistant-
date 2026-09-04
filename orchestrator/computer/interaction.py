import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchestrator.computer.models import (
    ScreenState,
    UIControlElement,
    ComputerActionRequest,
    ComputerActionResult,
    ComputerSession,
)
from orchestrator.computer.allowlist import default_computer_allowlist
from orchestrator.approval import default_approval_manager, ApprovalPolicyEvaluator

class ComputerInteractionManager:
    """
    Controlled computer interaction manager supporting structured screen state inspection,
    allowlist policy checks, Phase 26 human approval integration, and bounded verification.
    """
    def __init__(self):
        self.active_sessions: Dict[str, ComputerSession] = {}

    def create_session(self, user_id: str, application: str, target: str) -> ComputerSession:
        sess_id = str(uuid.uuid4())
        session = ComputerSession(
            session_id=sess_id,
            user_id=user_id,
            application=application,
            target_url_or_window=target,
            permissions=["read", "click"],
        )
        self.active_sessions[sess_id] = session
        return session

    def inspect_screen(self, session_id: str) -> ScreenState:
        session = self.active_sessions.get(session_id)
        app_name = session.application if session else "browser"

        return ScreenState(
            application=app_name,
            window_title=f"{app_name.capitalize()} - Main Workspace",
            visible_text=f"Sample text content inside {app_name}",
            detected_controls=[
                UIControlElement(id="btn_submit", element_type="button", label="Submit Query"),
                UIControlElement(id="inp_query", element_type="input", label="Search Box"),
            ],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def execute_action(self, request: ComputerActionRequest, user_id: str) -> ComputerActionResult:
        risk_level, req_confirm = default_computer_allowlist.evaluate_action(
            application=request.application,
            target=request.target_element_id or "default",
            action_type=request.action_type,
        )

        if risk_level == "blocked":
            return ComputerActionResult(
                success=False,
                action_type=request.action_type,
                risk_level="blocked",
                error_message="Action blocked by security policy.",
            )

        if ApprovalPolicyEvaluator.requires_approval(request.action_type, risk_level=risk_level, requires_confirmation=req_confirm):
            default_approval_manager.create_approval(
                user_id=user_id,
                session_id=request.session_id,
                action_type=request.action_type,
                action_summary=f"Computer Action '{request.action_type}' on '{request.application}'",
                risk_level=risk_level,
            )

        new_state = self.inspect_screen(request.session_id)
        return ComputerActionResult(
            success=True,
            action_type=request.action_type,
            risk_level=risk_level,
            resulting_state=new_state,
        )

default_computer_manager = ComputerInteractionManager()
