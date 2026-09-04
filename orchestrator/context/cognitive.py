"""
Phase 66: Cognitive Architecture 2.0 & Context Priority Engine.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from orchestrator.context.models import ConversationContext
from orchestrator.memory import default_memory_manager

class CognitiveContext(BaseModel):
    """Unified cognitive context integrating working memory, episodic history, project context, and constraints."""
    user_id: str
    session_id: str
    current_request: str = ""
    current_goal: Optional[str] = None
    current_task: Optional[str] = None
    working_context: Dict[str, Any] = Field(default_factory=dict)
    recent_context: List[Dict[str, Any]] = Field(default_factory=list)
    episodic_context: List[Dict[str, Any]] = Field(default_factory=list)
    semantic_context: List[str] = Field(default_factory=list)
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    project_context: Dict[str, Any] = Field(default_factory=dict)
    relevant_memory: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_knowledge: List[str] = Field(default_factory=list)
    active_constraints: List[str] = Field(default_factory=list)
    uncertainty: float = 0.0
    version: int = 1

class CognitiveManager:
    """Manages cognitive context prioritization, compression, conflict detection, and state versioning."""

    def assemble_cognitive_context(
        self,
        user_id: str,
        session_id: str,
        current_request: str,
        working_data: Optional[Dict[str, Any]] = None,
        goal_description: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> CognitiveContext:

        # Fetch relevant memories
        memories = default_memory_manager.get_relevant_memories(user_id=user_id, query=current_request)
        mem_dicts = [{"id": m.id, "content": m.content, "importance": m.importance} for m in memories]


        cog = CognitiveContext(
            user_id=user_id,
            session_id=session_id,
            current_request=current_request,
            current_goal=goal_description,
            working_context=working_data or {},
            relevant_memory=mem_dicts,
            active_constraints=["Preserve user authorization", "Strict budget limits"]
        )

        return cog

    def compress_cognitive_context(self, context: CognitiveContext) -> Dict[str, Any]:
        """Compresses long cognitive state into compact key facts, decisions, and constraints."""
        key_facts = []
        if context.current_request:
            key_facts.append(f"Request: {context.current_request[:100]}")
        if context.current_goal:
            key_facts.append(f"Goal: {context.current_goal[:100]}")

        for m in context.relevant_memory[:3]:
            key_facts.append(f"Memory: {m.get('content')}")

        return {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "key_facts": key_facts,
            "active_constraints": context.active_constraints,
            "version": context.version
        }

    def detect_cognitive_conflicts(self, context: CognitiveContext, new_fact: str) -> Dict[str, Any]:
        """Detects conflicts between existing cognitive memories and incoming information."""
        conflicts = []
        new_fact_lower = new_fact.lower()

        for m in context.relevant_memory:
            content_lower = m.get("content", "").lower()
            if "not " in new_fact_lower and new_fact_lower.replace("not ", "").strip() in content_lower:
                conflicts.append({"existing": m.get("content"), "new": new_fact})
            elif "not " in content_lower and content_lower.replace("not ", "").strip() in new_fact_lower:
                conflicts.append({"existing": m.get("content"), "new": new_fact})

        if conflicts:
            context.uncertainty = 0.85
            return {"status": "CONFLICT_DETECTED", "conflicts": conflicts, "uncertainty": 0.85}

        return {"status": "NO_CONFLICT", "conflicts": [], "uncertainty": context.uncertainty}

default_cognitive_manager = CognitiveManager()
