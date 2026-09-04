import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from orchestrator.jobs.models import Job
from orchestrator.tools import default_executor
from orchestrator.research import default_source_ranker, default_research_synthesizer
from orchestrator.knowledge import default_vector_store, default_embedding_provider, KnowledgeChunk

logger = logging.getLogger(__name__)

class BaseJobHandler(ABC):
    """
    Abstract interface for background job execution handlers.
    """
    @abstractmethod
    async def execute(self, job: Job, update_progress: Callable[[int, str], None]) -> str:
        pass

class ResearchJobHandler(BaseJobHandler):
    """
    Executes long-running web research, source ranking, and synthesis asynchronously.
    """
    async def execute(self, job: Job, update_progress: Callable[[int, str], None]) -> str:
        query_str = job.result or "JARVIS architecture"

        # 25% Progress - Web Search
        update_progress(25, f"Searching web for '{query_str}'...")
        await asyncio.sleep(0.1)

        tool_res = default_executor.execute("web_search", query=query_str)
        if not tool_res.success or not isinstance(tool_res.output, list):
            raise RuntimeError(f"Web search failed: {tool_res.error}")

        # 50% Progress - Source Ranking
        update_progress(50, f"Ranking {len(tool_res.output)} web sources...")
        await asyncio.sleep(0.1)

        ranked_sources = default_source_ranker.rank_sources(query_str, tool_res.output)

        # 75% Progress - Evidence Synthesis
        update_progress(75, "Synthesizing evidence-based research answer...")
        syn_result = await default_research_synthesizer.synthesize(query_str, ranked_sources)

        # 100% Progress - Completed
        update_progress(100, "Research synthesis completed.")
        return syn_result.summary

class DocumentIngestionJobHandler(BaseJobHandler):
    """
    Executes document chunking and vector store embedding ingestion asynchronously.
    """
    async def execute(self, job: Job, update_progress: Callable[[int, str], None]) -> str:
        doc_content = job.result or "Default document content"
        doc_name = "uploaded_doc.md"

        # 30% Progress - Chunking
        update_progress(30, f"Splitting document '{doc_name}' into chunks...")
        await asyncio.sleep(0.1)

        chunk = KnowledgeChunk(content=doc_content, source=doc_name)

        # 70% Progress - Embeddings
        update_progress(70, "Computing vector embeddings...")
        default_vector_store.add_chunks([chunk], embedding_provider=default_embedding_provider)

        # 100% Progress - Completed
        update_progress(100, "Ingestion completed.")
        return f"Successfully ingested 1 chunk from '{doc_name}' into knowledge vector store."

JOB_HANDLERS: Dict[str, BaseJobHandler] = {
    "research": ResearchJobHandler(),
    "document_ingestion": DocumentIngestionJobHandler(),
}
