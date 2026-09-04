import os
from typing import Any, Dict, List, Optional

class RepositoryInspector:
    """
    Safe repository inspection interface with path traversal defense, file limits,
    and sensitive configuration protection.
    """
    PROTECTED_PATTERNS = [".env", ".git", "id_rsa", "credentials", "secret"]

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)

    def _validate_path(self, rel_path: str) -> str:
        abs_path = os.path.abspath(os.path.join(self.root_dir, rel_path))
        if not abs_path.startswith(self.root_dir):
            raise PermissionError(f"Path traversal access denied: '{rel_path}'")

        basename = os.path.basename(abs_path).lower()
        if any(pat in basename for pat in self.PROTECTED_PATTERNS):
            raise PermissionError(f"Access to sensitive file '{rel_path}' is protected.")

        return abs_path

    def list_files(self, rel_dir: str = ".", max_files: int = 100) -> List[str]:
        target_dir = self._validate_path(rel_dir)
        files_found = []

        for root, dirs, files in os.walk(target_dir):
            # Ignore hidden and build directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "dist", "venv", "__pycache__"}]
            for f in files:
                if len(files_found) >= max_files:
                    break
                full_path = os.path.join(root, f)
                rel = os.path.relpath(full_path, self.root_dir)
                files_found.append(rel.replace("\\", "/"))
        return files_found

    def read_file(self, rel_path: str, max_bytes: int = 100000) -> str:
        target_file = self._validate_path(rel_path)
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"File '{rel_path}' not found.")

        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)

    def detect_project_type(self) -> Dict[str, Any]:
        files = self.list_files(".", max_files=50)
        has_py = any(f.endswith(".py") for f in files)
        has_js = any(f.endswith(".js") or f.endswith(".ts") or f == "package.json" for f in files)

        return {
            "languages": [l for l, cond in [("python", has_py), ("javascript/typescript", has_js)] if cond],
            "has_tests": any("test" in f for f in files),
        }
