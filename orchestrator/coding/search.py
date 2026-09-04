from typing import Any, Dict, List
from orchestrator.coding.repository import RepositoryInspector

class CodeSearchEngine:
    """
    Performs targeted code symbol and keyword search across non-ignored workspace files.
    """
    def __init__(self, inspector: RepositoryInspector):
        self.inspector = inspector

    def search_text(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not query:
            return []

        files = self.inspector.list_files(".", max_files=100)
        matches = []
        q_lower = query.lower()

        for f_rel in files:
            if len(matches) >= max_results:
                break
            try:
                content = self.inspector.read_file(f_rel)
                if q_lower in content.lower():
                    lines = content.splitlines()
                    for idx, line in enumerate(lines, 1):
                        if q_lower in line.lower():
                            matches.append({
                                "file": f_rel,
                                "line_number": idx,
                                "content": line.strip(),
                            })
                            if len(matches) >= max_results:
                                break
            except Exception:
                continue

        return matches
