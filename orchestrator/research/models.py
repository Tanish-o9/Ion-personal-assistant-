from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

MAX_RESEARCH_SOURCES = 5
MAX_SOURCE_CONTENT_LENGTH = 2000

class ResearchSource:
    """
    Represents a single web research source.
    """
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        relevance_score: float = 0.0,
        content: Optional[str] = None,
    ):
        self.title = title.strip() if title else "Untitled Source"
        self.url = self.normalize_url(url)
        self.snippet = snippet.strip() if snippet else ""
        self.relevance_score = relevance_score
        self.content = (content or snippet or "")[:MAX_SOURCE_CONTENT_LENGTH]

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalizes URLs to facilitate duplicate detection.
        """
        if not url:
            return ""
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        normalized = f"{scheme}://{netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchSource":
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            snippet=data.get("snippet", ""),
            relevance_score=data.get("relevance_score", 0.0),
            content=data.get("content"),
        )

class ResearchFinding:
    """
    Represents a single evidence-based claim supported by sources.
    """
    def __init__(
        self,
        claim: str,
        supporting_sources: Optional[List[str]] = None,
        confidence: str = "medium",
    ):
        self.claim = claim.strip()
        self.supporting_sources = supporting_sources or []
        self.confidence = confidence if confidence in {"high", "medium", "low"} else "medium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "supporting_sources": self.supporting_sources,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchFinding":
        return cls(
            claim=data.get("claim", ""),
            supporting_sources=data.get("supporting_sources", []),
            confidence=data.get("confidence", "medium"),
        )

class ResearchResult:
    """
    Encapsulates the complete structured result of a research operation.
    """
    def __init__(
        self,
        query: str,
        sources: Optional[List[ResearchSource]] = None,
        findings: Optional[List[ResearchFinding]] = None,
        summary: str = "",
    ):
        self.query = query
        self.sources = sources or []
        self.findings = findings or []
        self.summary = summary.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "sources": [s.to_dict() for s in self.sources],
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchResult":
        return cls(
            query=data.get("query", ""),
            sources=[ResearchSource.from_dict(s) for s in data.get("sources", [])],
            findings=[ResearchFinding.from_dict(f) for f in data.get("findings", [])],
            summary=data.get("summary", ""),
        )
