from typing import Any, Dict, List
from orchestrator.documents.pipeline import ParsedDocument

class DocumentComparisonResult:
    def __init__(self, doc1_name: str, doc2_name: str, added: List[str], removed: List[str], modified: List[str]):
        self.doc1_name = doc1_name
        self.doc2_name = doc2_name
        self.added = added
        self.removed = removed
        self.modified = modified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc1": self.doc1_name,
            "doc2": self.doc2_name,
            "added_sections": self.added,
            "removed_sections": self.removed,
            "modified_sections": self.modified,
        }

class DocumentComparator:
    """
    Compares two parsed documents and returns structural section differences.
    """
    @staticmethod
    def compare(doc1: ParsedDocument, doc2: ParsedDocument) -> DocumentComparisonResult:
        sec1_map = {s.title or f"sec_{idx}": s.content for idx, s in enumerate(doc1.sections)}
        sec2_map = {s.title or f"sec_{idx}": s.content for idx, s in enumerate(doc2.sections)}

        added = [t for t in sec2_map if t not in sec1_map]
        removed = [t for t in sec1_map if t not in sec2_map]
        modified = [t for t in sec1_map if t in sec2_map and sec1_map[t] != sec2_map[t]]

        return DocumentComparisonResult(
            doc1_name=doc1.filename,
            doc2_name=doc2.filename,
            added=added,
            removed=removed,
            modified=modified,
        )
