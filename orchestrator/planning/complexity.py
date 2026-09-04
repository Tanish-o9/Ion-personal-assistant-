import re
from typing import Any, Dict, Optional

class ComplexityAssessor:
    """
    Assesses task complexity and assigns an optimal execution route.
    Routes:
    - direct_response: Simple chit-chat / single-shot questions
    - single_tool: Single deterministic tool query (e.g. arithmetic, direct search)
    - multi_step_task: Multi-stage workflow requiring step planning
    - research_task: Web research and multi-source synthesis
    - knowledge_task: Vector knowledge base RAG retrieval
    - background_task: Long-running task suited for background worker processing
    - multimodal_task: Visual or document understanding task
    """
    @staticmethod
    def assess_route(
        text: str,
        has_files: bool = False,
        is_background: bool = False,
        intent: Optional[str] = None,
    ) -> str:
        if is_background:
            return "background_task"

        if has_files:
            return "multimodal_task"

        if not text or not text.strip():
            return "direct_response"

        lowered = text.lower().strip()
        words = lowered.split()

        # 1. Multi-step task triggers check (takes priority over single math if triggers present)
        multi_step_triggers = [
            "and then", "and explain", "and compare", "and check", "and summarize", "then tell me", "step by step"
        ]
        if any(t in lowered for t in multi_step_triggers) or len(words) > 25:
            return "multi_step_task"

        # 2. Fast-path math / single tool check
        if any(op in lowered for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided by", "calculate"]):
            if any(char.isdigit() for char in lowered):
                return "single_tool"

        # 3. RAG / Internal knowledge check
        if any(kw in lowered for kw in ["knowledge base", "internal doc", "my notes", "saved document", "rag"]):
            return "knowledge_task"

        # 4. Research task check
        research_keywords = ["search the web", "research", "compare", "latest news", "find sources", "look up"]
        if any(kw in lowered for kw in research_keywords) or intent == "research_task":
            return "research_task"

        # 5. Short direct response default
        if len(words) <= 8 and not any(char in lowered for char in ["?", "!"]):
            return "direct_response"

        return "direct_response"
