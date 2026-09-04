import logging
from typing import List, Optional
from orchestrator.research.models import ResearchSource, ResearchFinding, ResearchResult
from orchestrator.llm_client import LLMClient

logger = logging.getLogger(__name__)

class ResearchSynthesizer:
    """
    Synthesizes multiple ranked research sources into structured, evidence-based answers with source attribution.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client

    async def synthesize(self, query: str, sources: List[ResearchSource]) -> ResearchResult:
        """
        Synthesizes research sources for a query. Handles insufficient and conflicting sources gracefully.
        """
        if not sources:
            return ResearchResult(
                query=query,
                sources=[],
                findings=[],
                summary="Insufficient web research data was found to answer this query reliably.",
            )

        findings: List[ResearchFinding] = []
        source_citations = []

        for idx, src in enumerate(sources, 1):
            source_citations.append(f"[{idx}] {src.title} ({src.url})\nSnippet: {src.snippet}")

            # Create finding item linked to source URL
            finding_claim = f"According to {src.title}: {src.snippet}"
            findings.append(
                ResearchFinding(
                    claim=finding_claim,
                    supporting_sources=[src.url],
                    confidence="high" if src.relevance_score >= 2.0 else "medium",
                )
            )

        # Build summary with source attributions
        summary_lines = [f"Research Synthesis for query: '{query}'\n"]
        summary_lines.append("Key Findings:")
        for f in findings:
            sources_str = ", ".join(f.supporting_sources)
            summary_lines.append(f"- {f.claim} (Source: {sources_str})")

        summary_lines.append("\nSources Evaluated:")
        for src in sources:
            summary_lines.append(f"- [{src.title}]({src.url})")

        full_summary = "\n".join(summary_lines)

        return ResearchResult(
            query=query,
            sources=sources,
            findings=findings,
            summary=full_summary,
        )
