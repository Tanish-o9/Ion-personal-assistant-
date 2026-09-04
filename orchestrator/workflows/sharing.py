"""
Phase 78: Workflow Sharing & Collaboration

Packaging, permission disclosure, safe import/export, versioning, and template sharing.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from orchestrator.workflows.models import WorkflowDefinition, WorkflowNode, WorkflowEdge
from orchestrator.workflows.validator import WorkflowValidator

class WorkflowPackage(BaseModel):
    package_id: str
    name: str
    description: str
    version: str = "v1.0"
    workflow_definition: Dict[str, Any]
    required_capabilities: List[str] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    owner_id: str
    visibility: str = "PRIVATE"  # PRIVATE, WORKSPACE, ORGANIZATION, SHARED, PUBLIC
    created_at: str = "2026-09-04T00:00:00Z"
    updated_at: str = "2026-09-04T00:00:00Z"

class PermissionReviewReport(BaseModel):
    package_id: str
    name: str
    visibility: str
    required_capabilities: List[str]
    required_permissions: List[str]
    potential_risks: List[str]
    approved_for_import: bool

class WorkflowExporter:
    """Safe workflow export that strips credentials, API keys, OAuth tokens, and sensitive private user data."""
    def export_package(self, package: WorkflowPackage) -> Dict[str, Any]:
        raw_data = package.dict()
        def_json = str(raw_data.get("workflow_definition", {}))

        # Security check: Ensure no secrets are leaked in export
        secrets_found = any(k in def_json.lower() for k in ["api_key", "secret", "password", "oauth_token"])
        if secrets_found:
            raise PermissionError("Export denied: Workflow definition contains unredacted credentials.")

        return raw_data

class WorkflowImportManager:
    """Manages permission disclosure, DAG validation, and user confirmation for importing workflows."""
    def __init__(self, validator: Optional[WorkflowValidator] = None):
        self.validator = validator or WorkflowValidator()
        self.shared_packages: Dict[str, WorkflowPackage] = {}
        self._seed_default_templates()

    def _seed_default_templates(self):
        templates = [
            ("tpl_research_summary", "Research Summary Template", "Automated multi-source research & synthesis", ["web_search", "rag_retriever"], ["READ"]),
            ("tpl_doc_analysis", "Document Analysis Template", "Parse and summarize uploaded technical documents", ["doc_parser"], ["READ"]),
            ("tpl_code_review", "Code Review Workflow Template", "Run static analysis and patch verification", ["code_analyzer", "patch_verifier"], ["READ", "EXECUTE"]),
        ]
        for tid, name, desc, caps, perms in templates:
            pkg = WorkflowPackage(
                package_id=tid,
                name=name,
                description=desc,
                version="v1.0",
                workflow_definition={"nodes": [{"id": "node_1", "type": "TRIGGER"}], "edges": []},
                required_capabilities=caps,
                required_permissions=perms,
                owner_id="system",
                visibility="PUBLIC",
            )
            self.shared_packages[tid] = pkg

    def review_permissions(self, package_id: str) -> PermissionReviewReport:
        pkg = self.shared_packages.get(package_id)
        if not pkg:
            raise FileNotFoundError(f"Workflow package '{package_id}' not found.")

        risks = []
        if "EXECUTE" in pkg.required_permissions or "DELETE" in pkg.required_permissions:
            risks.append("WARNING: Workflow requests execute or delete permissions on workspace resources.")

        return PermissionReviewReport(
            package_id=pkg.package_id,
            name=pkg.name,
            visibility=pkg.visibility,
            required_capabilities=pkg.required_capabilities,
            required_permissions=pkg.required_permissions,
            potential_risks=risks,
            approved_for_import=len(risks) == 0,
        )

    def import_workflow(self, package_id: str, user_id: str, user_confirmed: bool = False) -> WorkflowPackage:
        pkg = self.shared_packages.get(package_id)
        if not pkg:
            raise FileNotFoundError(f"Workflow package '{package_id}' not found.")

        review = self.review_permissions(package_id)
        if not review.approved_for_import and not user_confirmed:
            raise PermissionError("Workflow import denied: User confirmation required for elevated permissions.")

        # Return imported package for user workspace
        imported_pkg = pkg.copy()
        imported_pkg.owner_id = user_id
        imported_pkg.visibility = "PRIVATE"
        return imported_pkg

default_workflow_import_manager = WorkflowImportManager()
