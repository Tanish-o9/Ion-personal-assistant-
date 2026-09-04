from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ConversationContext(BaseModel):
    """
    Structured representation of active conversation context.
    """
    session_id: str
    user_id: str
    current_topic: Optional[str] = None
    active_task: Optional[str] = None
    recent_messages: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_summary: Optional[str] = None
    unresolved_items: List[str] = Field(default_factory=list)
    active_entities: Dict[str, str] = Field(default_factory=dict)
    estimated_tokens: int = 0
    last_updated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_topic": self.current_topic,
            "active_task": self.active_task,
            "recent_messages": self.recent_messages,
            "conversation_summary": self.conversation_summary,
            "unresolved_items": self.unresolved_items,
            "active_entities": self.active_entities,
            "estimated_tokens": self.estimated_tokens,
            "last_updated": self.last_updated,
        }
