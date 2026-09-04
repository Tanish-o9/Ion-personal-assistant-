import pytest
from orchestrator.coding.engineer import (
    SoftwareEngineerEngine,
    RepoIndexManager,
    SafeGitManager,
    SoftwareMemoryManager,
    default_software_engineer_engine,
)
from orchestrator.coding.repository import RepositoryInspector

def test_repo_index_manager():
    inspector = RepositoryInspector()
    index_mgr = RepoIndexManager(inspector)
    structure = index_mgr.build_index(max_files=50)
    assert structure.total_files_indexed > 0
    assert "python" in structure.languages or "javascript/typescript" in structure.languages

def test_software_engineer_flow():
    engine = SoftwareEngineerEngine()
    result = engine.run_software_task(
        issue_description="Fix bug in context manager memory leaks",
        file_target="orchestrator/context/manager.py",
        new_code="# Updated context manager code\n",
        issue_type="Bug",
    )
    assert result["stage_status"] in {"VERIFIED", "REVIEW_FAILED"}
    assert "patch" in result
    assert "test_result" in result
    assert "review" in result
    assert "benchmark" in result

def test_safe_git_and_memory():
    git_mgr = SafeGitManager()
    status = git_mgr.get_status()
    assert status["auto_push_enabled"] is False

    mem_mgr = SoftwareMemoryManager()
    mem_mgr.record_decision("proj-1", "Use Pydantic v2", "Performance and strict validation")
    convs = mem_mgr.get_conventions("proj-1")
    assert len(convs) == 1
    assert convs[0]["decision"] == "Use Pydantic v2"
