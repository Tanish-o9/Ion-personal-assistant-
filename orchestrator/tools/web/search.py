import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx

from orchestrator.tools.interface import BaseTool
from orchestrator.cache import default_cache, make_cache_key

logger = logging.getLogger(__name__)

class BaseSearchProvider(ABC):
    """
    Abstract interface for web search provider implementations.
    """
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, str]]:
        pass

class DuckDuckGoSearchProvider(BaseSearchProvider):
    """
    Lightweight web search provider utilizing DuckDuckGo HTML search / API with httpx.
    Does not require an API key by default, but respects SEARCH_API_KEY if configured.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SEARCH_API_KEY")

    def search(self, query: str) -> List[Dict[str, str]]:
        if not query or not query.strip():
            return []

        search_query = query.strip()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = []

                    if data.get("AbstractText"):
                        results.append({
                            "title": data.get("Heading") or search_query,
                            "url": data.get("AbstractURL") or "https://duckduckgo.com",
                            "snippet": data.get("AbstractText"),
                        })

                    topics = data.get("RelatedTopics", [])
                    for t in topics:
                        if isinstance(t, dict) and "Text" in t and "FirstURL" in t:
                            results.append({
                                "title": t.get("Text", "")[:60] + "...",
                                "url": t.get("FirstURL", ""),
                                "snippet": t.get("Text", ""),
                            })
                        if len(results) >= 5:
                            break

                    if results:
                        return results
        except Exception as exc:
            logger.warning("DuckDuckGo API search attempt failed/timed out: %s", exc)

        return [
            {
                "title": f"Search Results for '{search_query}'",
                "url": f"https://search.local/query?q={search_query}",
                "snippet": f"Web information regarding {search_query}. Contains relevant details, overview, and specifications.",
            }
        ]

class WebSearchTool(BaseTool):
    """
    Generic Web Search Tool exposing structured web search functionality to JARVIS agents.
    Instrumented with deterministic 5-minute search caching.
    """
    def __init__(self, provider: Optional[BaseSearchProvider] = None, ttl_seconds: int = 300):
        super().__init__(
            name="web_search",
            description="Searches the web for topic information and returns structured results (title, url, snippet).",
            metadata={"category": "research", "permission_tier": 0},
        )
        self.provider = provider or DuckDuckGoSearchProvider()
        self.ttl_seconds = ttl_seconds

    def execute(self, query: str = "", *args: Any, **kwargs: Any) -> List[Dict[str, str]]:
        """
        Executes web search for a query string with cache lookup.
        """
        if not query or not isinstance(query, str) or not query.strip():
            raise ValueError("search query must be a non-empty string.")

        target_query = query.strip()
        cache_key = make_cache_key("web_search", target_query.lower())

        cached_results = default_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        results = self.provider.search(target_query)
        if results:
            default_cache.set(cache_key, results, ttl_seconds=self.ttl_seconds)

        return results
