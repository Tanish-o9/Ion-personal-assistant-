from typing import List

class ResearchDecomposer:
    """
    Decomposes complex research queries into focused, bounded subqueries.
    Simple queries bypass decomposition automatically.
    """
    @staticmethod
    def decompose_query(query: str, max_subqueries: int = 4) -> List[str]:
        q_lower = query.lower().strip()
        words = q_lower.split()

        # Simple queries bypass decomposition
        if len(words) < 6 and not any(w in q_lower for w in ["compare", "vs", "difference", "impact", "analysis"]):
            return [query]

        subqueries = [query]
        if "compare" in q_lower or "vs" in q_lower:
            parts = q_lower.replace("compare", "").split(" vs ")
            if len(parts) == 2:
                subqueries.append(f"overview of {parts[0].strip()}")
                subqueries.append(f"overview of {parts[1].strip()}")
        elif "impact" in q_lower:
            subqueries.append(f"benefits of {query}")
            subqueries.append(f"risks and challenges of {query}")

        return subqueries[:max_subqueries]
