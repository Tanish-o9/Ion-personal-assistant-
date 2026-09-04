import pytest
from orchestrator.coding import RepositoryInspector, CodeSearchEngine, PatchGenerator

def test_repository_inspector_security():
    inspector = RepositoryInspector(root_dir=".")

    # 1. Path traversal defense
    with pytest.raises(PermissionError):
        inspector.read_file("../../etc/passwd")

    # 2. Protected sensitive files
    with pytest.raises(PermissionError):
        inspector.read_file(".env")

def test_repository_listing_and_detection():
    inspector = RepositoryInspector(root_dir=".")
    files = inspector.list_files(".", max_files=10)
    assert isinstance(files, list)

    proj_type = inspector.detect_project_type()
    assert "languages" in proj_type

def test_code_search_and_patch():
    inspector = RepositoryInspector(root_dir=".")
    search_engine = CodeSearchEngine(inspector)

    results = search_engine.search_text("RepositoryInspector", max_results=5)
    assert isinstance(results, list)

    # Patch generation
    orig = "def hello():\n    print('world')\n"
    new = "def hello():\n    print('JARVIS')\n"
    patch = PatchGenerator.generate_patch("sample.py", orig, new)

    assert patch.file_path == "sample.py"
    assert "JARVIS" in patch.diff
