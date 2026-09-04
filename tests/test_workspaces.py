import pytest
from orchestrator.workspaces import default_workspace_manager

def test_workspace_creation_and_invitation_flow():
    owner_id = "u_ws_owner"
    guest_id = "u_ws_guest"

    # Create workspace
    ws = default_workspace_manager.create_workspace("AI Team Workspace", owner_id=owner_id)
    assert ws.name == "AI Team Workspace"
    assert ws.owner_id == owner_id

    # Owner generates invitation
    inv = default_workspace_manager.create_invitation(ws.id, user_id=owner_id, role="EDITOR")
    assert inv.token.startswith("inv_")

    # Guest accepts invitation
    member = default_workspace_manager.accept_invitation(inv.token, user_id=guest_id)
    assert member.user_id == guest_id
    assert member.role == "EDITOR"

    # Guest permissions check
    assert default_workspace_manager.has_permission(ws.id, guest_id, "EDIT") is True
    assert default_workspace_manager.has_permission(ws.id, guest_id, "ADMIN") is False
