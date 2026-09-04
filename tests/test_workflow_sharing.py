import pytest
from orchestrator.workflows.sharing import (
    WorkflowPackage,
    WorkflowExporter,
    WorkflowImportManager,
    default_workflow_import_manager,
)

def test_workflow_package_and_export():
    pkg = WorkflowPackage(
        package_id="pkg-1",
        name="Custom Workflow",
        description="Test workflow package",
        version="v1.0",
        workflow_definition={"nodes": [], "edges": []},
        required_capabilities=["web_search"],
        required_permissions=["READ"],
        owner_id="usr-1",
        visibility="WORKSPACE",
    )
    exporter = WorkflowExporter()
    exported = exporter.export_package(pkg)
    assert exported["package_id"] == "pkg-1"

def test_workflow_export_credential_redaction_guard():
    pkg = WorkflowPackage(
        package_id="pkg-leak",
        name="Leaky Workflow",
        description="Test workflow package with secret",
        workflow_definition={"nodes": [{"id": "n1", "api_key": "secret_key_123"}]},
        owner_id="usr-1",
    )
    exporter = WorkflowExporter()
    with pytest.raises(PermissionError, match="unredacted credentials"):
        exporter.export_package(pkg)

def test_workflow_import_permission_review_and_import():
    mgr = WorkflowImportManager()
    
    # Review public template
    review = mgr.review_permissions("tpl_research_summary")
    assert review.approved_for_import is True
    assert "web_search" in review.required_capabilities

    # Import template for user
    imported = mgr.import_workflow("tpl_research_summary", user_id="user-42")
    assert imported.owner_id == "user-42"
    assert imported.visibility == "PRIVATE"
