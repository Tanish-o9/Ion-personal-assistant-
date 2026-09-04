from typing import Any, Dict, List, Optional, Tuple

class EntityResolver:
    """
    Resolves ambiguous entity references ("my AI project", "that document") against user projects, context, and memory.
    """
    @staticmethod
    def resolve_reference(
        reference: str,
        user_projects: List[Dict[str, Any]],
        recent_documents: List[str],
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        ref_lower = reference.lower().strip()

        # Match projects
        matching_projects = [
            p for p in user_projects
            if ref_lower in p.get("name", "").lower() or any(w in p.get("name", "").lower() for w in ref_lower.split())
        ]

        if len(matching_projects) == 1:
            return matching_projects[0], False
        elif len(matching_projects) > 1:
            return None, True # Ambiguous match found! Ask user for clarification.

        # Match documents
        matching_docs = [
            d for d in recent_documents
            if ref_lower in d.lower()
        ]
        if len(matching_docs) == 1:
            return {"name": matching_docs[0], "type": "document"}, False
        elif len(matching_docs) > 1:
            return None, True

        return None, False
