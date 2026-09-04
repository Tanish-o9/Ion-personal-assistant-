import re
from typing import Any, Dict, List, Optional
from orchestrator.research.models import ResearchSource, MAX_RESEARCH_SOURCES

class SourceRanker:
    """
    Ranks and deduplicates candidate research sources based on query relevance.
    """
    def __init__(self, max_sources: int = MAX_RESEARCH_SOURCES):
        self.max_sources = max_sources

    def calculate_relevance(self, query: str, title: str, snippet: str) -> float:
        """
        Calculates a deterministic relevance score for a source based on query keywords.
        """
        if not query:
            return 1.0

        stopwords = {"a", "an", "the", "is", "are", "what", "how", "why", "for", "to", "in", "of", "and", "or"}
        words = [w.lower() for w in re.findall(r"\w+", query) if w.lower() not in stopwords and len(w) > 2]

        if not words:
            return 1.0

        combined_text = f"{title} {snippet}".lower()
        matches = sum(1 for w in words if w in combined_text)

        # Title match bonus
        title_matches = sum(1 for w in words if w in title.lower())
        score = (matches * 2.0) + (title_matches * 1.5)

        # Quality completeness bonus
        if len(snippet) > 50:
            score += 0.5

        return score

    def rank_sources(self, query: str, raw_results: List[Dict[str, Any]]) -> List[ResearchSource]:
        """
        Deduplicates raw search results, calculates relevance scores, and returns top N ResearchSources.
        """
        if not raw_results:
            return []

        seen_urls = set()
        sources: List[ResearchSource] = []

        for item in raw_results:
            url = item.get("url", "")
            norm_url = ResearchSource.normalize_url(url)
            if not norm_url or norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)

            title = item.get("title", "")
            snippet = item.get("snippet", "")
            content = item.get("content", snippet)

            score = self.calculate_relevance(query, title, snippet)
            src = ResearchSource(
                title=title,
                url=norm_url,
                snippet=snippet,
                relevance_score=score,
                content=content,
            )
            sources.append(src)

        # Sort descending by relevance score
        sources.sort(key=lambda s: s.relevance_score, reverse=True)
        return sources[:self.max_sources]
