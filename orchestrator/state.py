from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langgraph.graph import add_messages

class OrchestratorState(TypedDict):
    """
    Shared state TypedDict for LangGraph orchestrator supervisor graph.
    Extended in Phase 20 with adaptive routing, verification confidence, and decision traces.
    """
    messages: Annotated[List[Dict[str, Any]], add_messages]
    session_id: str
    user_id: str
    intent: str  # chat, coding_task, research_task, system_task, scheduling_task
    active_memory: List[Dict[str, Any]]
    emotion_state: Dict[str, Any]
    pending_action: Optional[Dict[str, Any]]
    final_response: Optional[str]
    subtasks: List[Dict[str, Any]]
    current_subtask_index: int

    # Tool System extensions (Phase 3)
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_results: Optional[List[Dict[str, Any]]]
    tool_round_count: int

    # Planning Engine extensions (Phase 6 & Phase 20)
    current_plan: Optional[Dict[str, Any]]
    plan_results: Optional[Dict[str, Any]]
    route: Optional[str]
    confidence: Optional[str]
    decision_trace: Optional[Dict[str, Any]]
    replan_count: Optional[int]

    # Research Engine extensions (Phase 8)
    research_sources: Optional[List[Dict[str, Any]]]
    research_findings: Optional[List[Dict[str, Any]]]
    research_summary: Optional[str]

    # RAG Knowledge Base extensions (Phase 9)
    retrieved_knowledge: Optional[List[Dict[str, Any]]]

    # Multimodal Input extensions (Phase 12)
    multimodal_inputs: Optional[List[Dict[str, Any]]]
    visual_context: Optional[str]
    document_context: Optional[str]
