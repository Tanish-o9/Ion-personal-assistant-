"""
Phase 58: Enterprise Organization Manager & Policy System.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from database.connection import get_db_context
from database.models import OrganizationModel, OrganizationMemberModel, WorkspaceModel, utc_now_iso

class OrganizationManager:
    """Manages enterprise organizations, org members, policies, and org-scoped workspace hierarchies."""

    def create_organization(self, owner_id: str, name: str, policies: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with get_db_context() as db:
            org_id = f"org_{uuid.uuid4().hex[:12]}"
            pol_json = json.dumps(policies or {
                "allowed_models": ["claude-3-5-sonnet", "gpt-4o"],
                "allowed_connectors": ["all"],
                "maximum_budget_usd": 100.0,
                "allowed_domains": ["*"]
            })
            org = OrganizationModel(
                id=org_id,
                name=name,
                owner_id=owner_id,
                policies_json=pol_json
            )
            db.add(org)

            # Add owner member record
            member = OrganizationMemberModel(
                id=str(uuid.uuid4()),
                org_id=org_id,
                user_id=owner_id,
                role="ORG_OWNER"
            )
            db.add(member)
            db.commit()
            db.refresh(org)

            return {
                "id": org.id,
                "name": org.name,
                "owner_id": org.owner_id,
                "policies": json.loads(org.policies_json or "{}"),
                "created_at": org.created_at
            }

    def get_organization(self, org_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        with get_db_context() as db:
            org = db.query(OrganizationModel).filter(OrganizationModel.id == org_id).first()
            if not org:
                return None
            member = db.query(OrganizationMemberModel).filter(
                OrganizationMemberModel.org_id == org_id,
                OrganizationMemberModel.user_id == user_id
            ).first()
            if not member and org.owner_id != user_id:
                return None

            return {
                "id": org.id,
                "name": org.name,
                "owner_id": org.owner_id,
                "policies": json.loads(org.policies_json or "{}"),
                "created_at": org.created_at
            }

    def add_workspace_to_org(self, workspace_id: str, org_id: str, user_id: str) -> bool:
        with get_db_context() as db:
            ws = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
            if not ws:
                return False
            ws.org_id = org_id
            db.commit()
            return True

    def validate_policy_compliance(self, org_id: str, model_name: str, requested_budget: float) -> bool:
        with get_db_context() as db:
            org = db.query(OrganizationModel).filter(OrganizationModel.id == org_id).first()
            if not org:
                return True # Default to allowed if no org policy bound
            pol = json.loads(org.policies_json or "{}")

            allowed_models = pol.get("allowed_models", [])
            max_budget = pol.get("maximum_budget_usd", 100.0)

            if allowed_models and "*" not in allowed_models and model_name not in allowed_models:
                return False
            if requested_budget > max_budget:
                return False

            return True

default_organization_manager = OrganizationManager()
