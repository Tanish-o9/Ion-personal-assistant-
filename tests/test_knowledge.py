import os
import tempfile
import pytest

from orchestrator.knowledge.models import KnowledgeChunk
from orchestrator.knowledge.loader import KnowledgeLoader
from orchestrator.knowledge.embeddings import SimpleEmbeddingProvider
from orchestrator.knowledge.vector_store import LocalVectorStore, cosine_similarity
from orchestrator.knowledge.retriever import KnowledgeRetriever, KnowledgeSearchTool, format_rag_context
from orchestrator.tools import default_registry, default_executor
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="RAG response based on retrieved knowledge context.",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. KnowledgeLoader Tests (.txt, .md, Chunking, Metadata)
# ---------------------------------------------------------------------------

def test_knowledge_loader_txt_and_md():
    loader = KnowledgeLoader(chunk_size=100, chunk_overlap=20)
    text = "Line 1 of sample documentation.\nLine 2 of sample documentation.\nLine 3 of sample documentation."

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "sample_notes.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        chunks = loader.load_file(filepath)
        assert len(chunks) >= 1
        assert chunks[0].source == "sample_notes.md"
        assert chunks[0].metadata["file_type"] == ".md"
        assert "documentation" in chunks[0].content

# ---------------------------------------------------------------------------
# 2. EmbeddingProvider Tests
# ---------------------------------------------------------------------------

def test_simple_embedding_provider():
    provider = SimpleEmbeddingProvider(vector_dim=64)
    emb1 = provider.embed("Python web programming")
    emb2 = provider.embed("Python web programming")
    emb3 = provider.embed("Cooking recipes for dinner")

    assert len(emb1) == 64
    assert emb1 == emb2  # Deterministic

    sim_same = cosine_similarity(emb1, emb2)
    sim_diff = cosine_similarity(emb1, emb3)
    assert sim_same > sim_diff

# ---------------------------------------------------------------------------
# 3. LocalVectorStore & Persistence Tests
# ---------------------------------------------------------------------------

def test_vector_store_save_load_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_vector_store.json")
        store = LocalVectorStore(storage_path=json_path)
        provider = SimpleEmbeddingProvider()

        c1 = KnowledgeChunk(content="Django is a Python web framework", source="django.md")
        c2 = KnowledgeChunk(content="FastAPI is an async Python web framework", source="fastapi.md")
        store.add_chunks([c1, c2], embedding_provider=provider)

        query_emb = provider.embed("Python web framework")
        results = store.search(query_emb, top_k=2)
        assert len(results) == 2
        assert results[0][0].source in {"django.md", "fastapi.md"}

        # Test Persistence reload
        reloaded_store = LocalVectorStore(storage_path=json_path)
        assert len(reloaded_store._chunks) == 2

# ---------------------------------------------------------------------------
# 4. KnowledgeRetriever & RAG Context Tests
# ---------------------------------------------------------------------------

def test_retriever_threshold_and_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_retriever_store.json")
        store = LocalVectorStore(storage_path=json_path)
        provider = SimpleEmbeddingProvider()

        c1 = KnowledgeChunk(content="Architecture guide for JARVIS AT SCALE", source="arch.md")
        store.add_chunks([c1], embedding_provider=provider)

        retriever = KnowledgeRetriever(vector_store=store, embedding_provider=provider, similarity_threshold=0.1)
        results = retriever.retrieve("JARVIS architecture")
        assert len(results) == 1

        formatted = format_rag_context(results)
        assert "Source: arch.md" in formatted
        assert "JARVIS AT SCALE" in formatted

        # Test tool execution
        tool = KnowledgeSearchTool(retriever=retriever)
        tool_res = tool.execute(query="JARVIS architecture")
        assert len(tool_res) == 1
        assert tool_res[0]["source"] == "arch.md"

def test_knowledge_search_registered_in_default_registry():
    tools = default_registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "knowledge_search" in tool_names

# ---------------------------------------------------------------------------
# 5. Graph RAG Integration Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_rag_integration():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "session-rag-test"}}

    inputs = {
        "messages": [{"role": "user", "content": "Tell me about JARVIS architecture"}],
        "session_id": "session-rag-test",
        "user_id": "test_rag_user",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    assert "retrieved_knowledge" in final_state
    messages = final_state.get("messages", [])
    assert len(messages) > 0
