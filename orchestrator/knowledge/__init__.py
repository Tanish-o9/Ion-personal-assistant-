from orchestrator.knowledge.models import KnowledgeChunk
from orchestrator.knowledge.loader import KnowledgeLoader
from orchestrator.knowledge.embeddings import BaseEmbeddingProvider, SimpleEmbeddingProvider
from orchestrator.knowledge.vector_store import LocalVectorStore
from orchestrator.knowledge.reranker import LightweightReranker, QueryRewriter
from orchestrator.knowledge.retriever import KnowledgeRetriever, KnowledgeSearchTool, format_rag_context

# Create shared default instances
default_embedding_provider = SimpleEmbeddingProvider()
default_vector_store = LocalVectorStore()
default_knowledge_loader = KnowledgeLoader()
default_knowledge_retriever = KnowledgeRetriever(
    vector_store=default_vector_store,
    embedding_provider=default_embedding_provider,
)

__all__ = [
    "KnowledgeChunk",
    "KnowledgeLoader",
    "BaseEmbeddingProvider",
    "SimpleEmbeddingProvider",
    "LocalVectorStore",
    "LightweightReranker",
    "QueryRewriter",
    "KnowledgeRetriever",
    "KnowledgeSearchTool",
    "format_rag_context",
    "default_embedding_provider",
    "default_vector_store",
    "default_knowledge_loader",
    "default_knowledge_retriever",
]
