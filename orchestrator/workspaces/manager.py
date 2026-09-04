import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from database.connection import get_db_context
from database.models import WorkspaceModel, WorkspaceMemberModel, WorkspaceInvitationModel, utc_now_iso
from orchestrator.workspaces.models import Workspace, WorkspaceMember, WorkspaceInvitation

class WorkspaceManager:
    """
    Manages workspace creation, invitations, roles, permissions, and collaborative resource scoping.
    """
    def create_workspace(self, name: str, owner_id: str) -> Workspace:
        ws_id = str(uuid.uuid4())
        with get_db_context() as db:
            ws = WorkspaceModel(id=ws_id, name=name, owner_id=owner_id)
            member = WorkspaceMemberModel(id=str(uuid.uuid4()), workspace_id=ws_id, user_id=owner_id, role="OWNER")
            db.add(ws)
            db.add(member)
            db.commit()
            db.refresh(ws)
            return Workspace(id=ws.id, name=ws.name, owner_id=ws.owner_id, created_at=ws.created_at)

    def create_invitation(self, workspace_id: str, user_id: str, role: str = "EDITOR", expires_in_hours: int = 48) -> WorkspaceInvitation:
        # Check permissions
        if not self.has_permission(workspace_id, user_id, "ADMIN"):
            raise PermissionError("Only workspace OWNER or ADMIN can generate invitations.")

        token = f"inv_{uuid.uuid4().hex}"
        inv_id = str(uuid.uuid4())
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).isoformat()

        with get_db_context() as db:
            inv = WorkspaceInvitationModel(
                id=inv_id,
                workspace_id=workspace_id,
                token=token,
                role=role,
                expires_at=expires_at,
            )
            db.add(inv)
            db.commit()
            return WorkspaceInvitation(id=inv.id, workspace_id=inv.workspace_id, token=inv.token, role=inv.role, expires_at=inv.expires_at)

    def accept_invitation(self, token: str, user_id: str) -> WorkspaceMember:
        with get_db_context() as db:
            inv = db.query(WorkspaceInvitationModel).filter(WorkspaceInvitationModel.token == token).first()
            if not inv:
                raise ValueError("Invalid invitation token.")

            now_iso = datetime.now(timezone.utc).isoformat()
            if inv.expires_at < now_iso:
                raise ValueError("Invitation token has expired.")

            member = db.query(WorkspaceMemberModel).filter(
                WorkspaceMemberModel.workspace_id == inv.workspace_id,
                WorkspaceMemberModel.user_id == user_id,
            ).first()

            if not member:
                member = WorkspaceMemberModel(
                    id=str(uuid.uuid4()),
                    workspace_id=inv.workspace_id,
                    user_id=user_id,
                    role=inv.role,
                )
                db.add(member)
                db.commit()
                db.refresh(member)

            return WorkspaceMember(id=member.id, workspace_id=member.workspace_id, user_id=member.user_id, role=member.role)

    def has_permission(self, workspace_id: str, user_id: str, required_action: str) -> bool:
        with get_db_context() as db:
            member = db.query(WorkspaceMemberModel).filter(
                WorkspaceMemberModel.workspace_id == workspace_id,
                WorkspaceMemberModel.user_id == user_id,
            ).first()

            if not member:
                return False

            role = member.role.upper()
            if role == "OWNER":
                return True
            if role == "EDITOR" and required_action in {"VIEW", "EDIT", "CREATE"}:
                return True
            if role == "VIEWER" and required_action in {"VIEW"}:
                return True
            return False

default_workspace_manager = WorkspaceManager()
