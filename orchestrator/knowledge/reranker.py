import re
from typing import List, Tuple
from orchestrator.knowledge.models import KnowledgeChunk

class LightweightReranker:
    """
    Reranks candidate retrieved chunks using a hybrid score of initial vector similarity
    and BM25 keyword matching overlap.
    """
    @staticmethod
    def rerank(
        query: str,
        candidates: List[Tuple[KnowledgeChunk, float]],
        top_k: int = 5,
    ) -> List[Tuple[KnowledgeChunk, float]]:
        if not candidates or not query:
            return candidates[:top_k]

        keywords = [w.lower().strip() for w in re.findall(r"\w+", query) if len(w) > 2]
        if not keywords:
            return sorted(candidates, key=lambda x: x[1], reverse=True)[:top_k]

        reranked = []
        for chunk, initial_score in candidates:
            text_lower = chunk.content.lower()
            keyword_matches = sum(1 for kw in keywords if kw in text_lower)
            keyword_score = keyword_matches / len(keywords)

            # Hybrid score weighting: 60% vector similarity + 40% keyword match
            hybrid_score = (0.6 * initial_score) + (0.4 * keyword_score)
            reranked.append((chunk, round(hybrid_score, 4)))

        return sorted(reranked, key=lambda x: x[1], reverse=True)[:top_k]

class QueryRewriter:
    """
    Transforms difficult questions into expanded, clean retrieval queries.
    """
    @staticmethod
    def rewrite_query(query: str) -> str:
        if not query or not query.strip():
            return query

        cleaned = query.strip()
        # Remove common query prefixes
        for prefix in ["what is ", "who is ", "tell me about ", "search for ", "find info on "]:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        return cleaned.strip()
