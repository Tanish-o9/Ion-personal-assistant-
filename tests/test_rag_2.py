import pytest
from orchestrator.knowledge import (
    KnowledgeChunk,
    KnowledgeRetriever,
    LocalVectorStore,
    SimpleEmbeddingProvider,
    LightweightReranker,
    QueryRewriter,
)

def test_knowledge_chunk_metadata_and_hashing():
    chunk = KnowledgeChunk(
        content="JARVIS System Architecture Overview",
        source="architecture.md",
        user_id="user_123",
        scope="project",
    )
    assert chunk.user_id == "user_123"
    assert chunk.scope == "project"
    assert chunk.content_hash is not None
    assert len(chunk.content_hash) == 64  # SHA256 hex string

def test_user_and_scope_isolation_retrieval():
    vstore = LocalVectorStore()
    provider = SimpleEmbeddingProvider()

    chunk_global = KnowledgeChunk(content="Public Python documentation", source="doc.txt", user_id="global", scope="global")
    chunk_userA = KnowledgeChunk(content="User A secret project roadmap", source="secret.txt", user_id="userA", scope="user")
    chunk_userB = KnowledgeChunk(content="User B financial statement", source="finance.txt", user_id="userB", scope="user")

    chunk_global.embedding = provider.embed(chunk_global.content)
    chunk_userA.embedding = provider.embed(chunk_userA.content)
    chunk_userB.embedding = provider.embed(chunk_userB.content)

    vstore.add([chunk_global, chunk_userA, chunk_userB])

    retriever = KnowledgeRetriever(vector_store=vstore, embedding_provider=provider, similarity_threshold=0.0)

    # User A retrieval: Should get global + userA chunks, NEVER userB chunks
    res_A = retriever.retrieve("secret roadmap documentation", user_id="userA")
    user_ids_retrieved_A = {c.user_id for c, _ in res_A}
    assert "userB" not in user_ids_retrieved_A

    # User B retrieval: Should NEVER get userA chunks
    res_B = retriever.retrieve("secret roadmap documentation", user_id="userB")
    user_ids_retrieved_B = {c.user_id for c, _ in res_B}
    assert "userA" not in user_ids_retrieved_B

def test_hybrid_reranker():
    chunk1 = KnowledgeChunk(content="Python Django web application development guide", source="s1")
    chunk2 = KnowledgeChunk(content="General software design patterns and principles", source="s2")

    candidates = [(chunk1, 0.5), (chunk2, 0.6)]
    reranked = LightweightReranker.rerank("Django web guide", candidates, top_k=2)

    # chunk1 has higher keyword overlap for "Django web guide"
    assert reranked[0][0].content == chunk1.content

def test_query_rewriter():
    assert QueryRewriter.rewrite_query("What is Python fast-path routing?") == "Python fast-path routing?"
    assert QueryRewriter.rewrite_query("tell me about Redis cache TTL") == "Redis cache TTL"
