import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from orchestrator.tools.interface import BaseTool
from orchestrator.tools.registry import ToolRegistry
from orchestrator.tools.executor import ToolExecutor
from orchestrator.tools.web import WebSearchTool, WebFetchTool, BaseSearchProvider, clean_html_to_text
from orchestrator.tools import default_registry
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockSearchProvider(BaseSearchProvider):
    def search(self, query: str):
        if query == "fail":
            raise RuntimeError("Provider connection failed")
        return [
            {
                "title": f"Official {query} Documentation",
                "url": f"https://docs.example.org/{query}",
                "snippet": f"Comprehensive guide and documentation for {query}.",
            }
        ]

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="Here is the research summary.",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. WebSearchTool Unit Tests
# ---------------------------------------------------------------------------

def test_web_search_tool_properties_and_execution():
    mock_provider = MockSearchProvider()
    search_tool = WebSearchTool(provider=mock_provider)

    assert search_tool.name == "web_search"
    results = search_tool.execute(query="Django")
    assert len(results) == 1
    assert results[0]["title"] == "Official Django Documentation"
    assert results[0]["url"] == "https://docs.example.org/Django"

def test_web_search_empty_query_validation():
    search_tool = WebSearchTool()
    with pytest.raises(ValueError, match="search query must be a non-empty string"):
        search_tool.execute(query="")

def test_web_search_provider_failure():
    mock_provider = MockSearchProvider()
    search_tool = WebSearchTool(provider=mock_provider)
    reg = ToolRegistry()
    reg.register(search_tool)
    executor = ToolExecutor(reg)

    res = executor.execute("web_search", query="fail")
    assert res.success is False
    assert "Provider connection failed" in res.error

# ---------------------------------------------------------------------------
# 2. WebFetchTool Unit Tests
# ---------------------------------------------------------------------------

def test_web_fetch_invalid_scheme():
    fetch_tool = WebFetchTool()
    with pytest.raises(ValueError, match="Invalid URL scheme 'file'"):
        fetch_tool.execute(url="file:///etc/passwd")

def test_web_fetch_empty_url():
    fetch_tool = WebFetchTool()
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        fetch_tool.execute(url="")

def test_clean_html_to_text():
    html = "<html><body><h1>Title</h1><p>Some paragraph text.</p><script>var x=1;</script></body></html>"
    cleaned = clean_html_to_text(html)
    assert "Title" in cleaned
    assert "Some paragraph text" in cleaned
    assert "var x=1" not in cleaned

@patch("httpx.Client.get")
def test_web_fetch_mocked_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = "https://example.com"
    mock_resp.content = b"<html><body><h1>Hello World</h1></body></html>"
    mock_resp.headers = {"content-type": "text/html"}
    mock_get.return_value = mock_resp

    fetch_tool = WebFetchTool()
    res = fetch_tool.execute(url="https://example.com")
    assert res["status_code"] == 200
    assert "Hello World" in res["content"]
    assert res["url"] == "https://example.com"

# ---------------------------------------------------------------------------
# 3. ToolRegistry Verification
# ---------------------------------------------------------------------------

def test_web_tools_registered_in_default_registry():
    tools = default_registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "web_search" in tool_names
    assert "web_fetch" in tool_names
    assert "calculator" in tool_names

# ---------------------------------------------------------------------------
# 4. Agent & Planner Integration Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_web_search_integration():
    mock_llm = MockLLM()
    graph = build_orchestrator_graph(mock_llm)
    config = {"configurable": {"thread_id": "session-web-1"}}

    inputs = {
        "messages": [{"role": "user", "content": "search for Django REST Framework"}],
        "session_id": "session-web-1",
        "user_id": "test_web_user",
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
    }

    final_state = await graph.ainvoke(inputs, config=config)
    messages = final_state.get("messages", [])
    last_content = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
    assert "Web research results" in last_content or "Django REST Framework" in last_content
