import pytest
from orchestrator.research.models import ResearchSource, ResearchFinding, ResearchResult, MAX_RESEARCH_SOURCES
from orchestrator.research.ranker import SourceRanker
from orchestrator.research.synthesizer import ResearchSynthesizer
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="Research summary mock output.",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. Research Model Tests
# ---------------------------------------------------------------------------

def test_research_models():
    src = ResearchSource(title="FastAPI Docs", url="https://fastapi.tiangolo.com/", snippet="FastAPI web framework", relevance_score=3.5)
    assert src.title == "FastAPI Docs"
    assert src.url == "https://fastapi.tiangolo.com"
    assert src.relevance_score == 3.5

    finding = ResearchFinding(claim="FastAPI is high performance", supporting_sources=[src.url], confidence="high")
    assert finding.confidence == "high"
    assert finding.supporting_sources == ["https://fastapi.tiangolo.com"]

    result = ResearchResult(query="FastAPI info", sources=[src], findings=[finding], summary="FastAPI summary")
    res_dict = result.to_dict()
    assert res_dict["query"] == "FastAPI info"
    assert len(res_dict["sources"]) == 1
    assert len(res_dict["findings"]) == 1

# ---------------------------------------------------------------------------
# 2. SourceRanker Tests (Relevance, Deduplication, Limits)
# ---------------------------------------------------------------------------

def test_source_ranker_deduplication_and_relevance():
    ranker = SourceRanker(max_sources=5)
    raw_results = [
        {"title": "Python Overview", "url": "https://python.org/doc", "snippet": "Official Python programming language documentation"},
        {"title": "Python Overview Duplicate", "url": "https://python.org/doc/", "snippet": "Duplicate entry"},
        {"title": "Java Guide", "url": "https://java.com/guide", "snippet": "Java language reference"},
    ]

    ranked = ranker.rank_sources("Python programming", raw_results)
    assert len(ranked) == 2  # Duplicate URL removed
    assert ranked[0].url == "https://python.org/doc"
    assert ranked[0].relevance_score > ranked[1].relevance_score

def test_source_ranker_bounded_limit():
    ranker = SourceRanker(max_sources=2)
    raw_results = [
        {"title": f"Doc {i}", "url": f"https://docs.org/item{i}", "snippet": f"Snippet details for item {i}"}
        for i in range(1, 10)
    ]
    ranked = ranker.rank_sources("details", raw_results)
    assert len(ranked) == 2

# ---------------------------------------------------------------------------
# 3. ResearchSynthesizer Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_research_synthesizer_multiple_sources():
    synthesizer = ResearchSynthesizer()
    sources = [
        ResearchSource(title="Django REST", url="https://django-rest.org", snippet="DRF provides REST API tools", relevance_score=3.0),
        ResearchSource(title="FastAPI", url="https://fastapi.tiangolo.com", snippet="FastAPI provides async web APIs", relevance_score=2.5),
    ]

    res = await synthesizer.synthesize("Python Web APIs", sources)
    assert res.query == "Python Web APIs"
    assert len(res.findings) == 2
    assert "django-rest.org" in res.summary
    assert "fastapi.tiangolo.com" in res.summary

@pytest.mark.asyncio
async def test_research_synthesizer_empty_sources():
    synthesizer = ResearchSynthesizer()
    res = await synthesizer.synthesize("Unknown topic", [])
    assert len(res.sources) == 0
    assert "Insufficient web research data" in res.summary

# ---------------------------------------------------------------------------
# 4. Graph Research Integration Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_research_synthesis_flow():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "session-research-synth"}}

    inputs = {
        "messages": [{"role": "user", "content": "search for Python web frameworks"}],
        "session_id": "session-research-synth",
        "user_id": "test_research_user",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    assert "research_sources" in final_state
    assert "research_findings" in final_state
    messages = final_state.get("messages", [])
    last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
    assert "Research Synthesis" in last_content or "Python web frameworks" in last_content
