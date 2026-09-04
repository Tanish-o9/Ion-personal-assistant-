import os
import logging
from typing import Any, Dict, List, Optional, Tuple

from orchestrator.knowledge.models import KnowledgeChunk
from orchestrator.knowledge.embeddings import BaseEmbeddingProvider, SimpleEmbeddingProvider
from orchestrator.knowledge.vector_store import LocalVectorStore
from orchestrator.knowledge.reranker import LightweightReranker, QueryRewriter
from orchestrator.tools.interface import BaseTool
from orchestrator.cache import default_cache, make_cache_key

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5
DEFAULT_SIMILARITY_THRESHOLD = 0.3

def format_rag_context(retrieved: List[Tuple[KnowledgeChunk, float]]) -> str:
    """
    Formats retrieved KnowledgeChunks into clean, prompt-ready LLM context with source attribution.
    """
    if not retrieved:
        return ""

    lines = ["Retrieved Knowledge Base Context:"]
    for chunk, score in retrieved:
        lines.append(f"\nSource: {chunk.source} (Relevance Score: {score:.2f})")
        lines.append(f"Content: {chunk.content}")

    return "\n".join(lines)

class KnowledgeRetriever:
    """
    Retrieves top-K relevant KnowledgeChunks matching a query from the vector store with scope/user filtering,
    query rewriting, hybrid reranking, and 30-minute RAG query caching.
    """
    def __init__(
        self,
        vector_store: Optional[LocalVectorStore] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self.vector_store = vector_store or LocalVectorStore()
        self.embedding_provider = embedding_provider or SimpleEmbeddingProvider()
        self.top_k = int(os.getenv("RAG_TOP_K", top_k))
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", similarity_threshold))

    def retrieve(
        self,
        query: str,
        user_id: str = "global",
        scope: Optional[str] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> List[Tuple[KnowledgeChunk, float]]:
        """
        Embeds query string, performs vector search with scope filtering and hybrid reranking.
        """
        if not query or not query.strip():
            return []

        rewritten_query = QueryRewriter.rewrite_query(query)
        clean_query = rewritten_query.lower()
        k = top_k if top_k is not None else self.top_k
        thresh = similarity_threshold if similarity_threshold is not None else self.similarity_threshold

        cache_key = make_cache_key("rag", f"u_{user_id}_sc_{scope}_k{k}", clean_query)
        cached_raw = default_cache.get(cache_key)
        if cached_raw is not None:
            reconstructed = []
            for item in cached_raw:
                c_dict, score = item
                chunk = KnowledgeChunk.from_dict(c_dict)
                reconstructed.append((chunk, score))
            return reconstructed

        query_emb = self.embedding_provider.embed(clean_query)
        raw_candidates = self.vector_store.search(query_emb, top_k=k * 2, min_score=thresh)

        # Apply strict User & Scope Isolation filtering
        filtered_candidates = []
        for chunk, score in raw_candidates:
            # User scope rule: global chunks OR matching user_id
            if chunk.user_id not in {"global", user_id}:
                continue
            if scope and chunk.scope != scope and chunk.scope != "global":
                continue
            filtered_candidates.append((chunk, score))

        # Perform hybrid reranking (60% vector + 40% keyword match)
        reranked = LightweightReranker.rerank(clean_query, filtered_candidates, top_k=k)

        if reranked:
            serializable = [(chunk.to_dict(), score) for chunk, score in reranked]
            default_cache.set(cache_key, serializable, ttl_seconds=1800)

        return reranked

class KnowledgeSearchTool(BaseTool):
    """
    Tool wrapping KnowledgeRetriever for discovery by JARVIS agents in ToolRegistry.
    """
    def __init__(self, retriever: Optional[KnowledgeRetriever] = None):
        super().__init__(
            name="knowledge_search",
            description="Searches the vector knowledge base for relevant documents and notes.",
            metadata={"category": "knowledge", "permission_tier": 0},
            capabilities=["knowledge", "search", "rag", "documents"],
            risk_level="low",
            latency_category="fast",
            cost_category="zero",
            cache_policy="SHORT_TTL",
            requires_network=False,
            suitable_for_background=True,
            input_schema={"query": "str", "scope": "str"},
        )
        self.retriever = retriever or KnowledgeRetriever()

    def execute(self, query: str = "", user_id: str = "global", scope: Optional[str] = None, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Executes knowledge search for a query string and returns structured chunks.
        """
        if not query or not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")

        retrieved = self.retriever.retrieve(query, user_id=user_id, scope=scope)
        return [
            {
                "chunk_id": chunk.id,
                "source": chunk.source,
                "title": chunk.title,
                "scope": chunk.scope,
                "content": chunk.content,
                "similarity": score,
            }
            for chunk, score in retrieved
        ]
