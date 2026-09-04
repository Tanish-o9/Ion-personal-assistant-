from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Workspace(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: str

class WorkspaceMember(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: str = "EDITOR" # OWNER, EDITOR, VIEWER

class WorkspaceInvitation(BaseModel):
    id: str
    workspace_id: str
    token: str
    role: str = "EDITOR"
    expires_at: str
