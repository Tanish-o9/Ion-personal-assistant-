import re
from datetime import datetime, timezone
from typing import List, Optional
from orchestrator.memory.store import BaseMemoryStore, InMemoryStore, MemoryRecord
from database.repository import MemoryRepository

MAX_ACTIVE_MEMORIES = 5

def score_memory_relevance(record: MemoryRecord, query: str, index: int, total_count: int) -> float:
    """
    Calculates a relevance score combining keyword matching, importance, and recency index.
    Formula: (keyword_matches * 3.0) + record.importance (1..5) + recency_bonus (0.1 per newer index)
    """
    importance_score = float(record.importance)
    recency_bonus = index * 0.1  # higher index = newer insertion

    if not query:
        return importance_score + recency_bonus

    stopwords = {
        "a", "an", "the", "is", "are", "what", "give", "me", "show", "for",
        "to", "in", "of", "and", "or", "it", "this", "that", "how", "i", "you", "can"
    }
    words = [w.lower() for w in re.findall(r"\w+", query) if w.lower() not in stopwords and len(w) > 2]

    content_lowered = record.content.lower()
    keyword_matches = sum(1 for w in words if w in content_lowered)

    return (keyword_matches * 3.0) + importance_score + recency_bonus

class MemoryManager:
    """
    Manages high-level memory operations: saving, scoring, ranking, user isolation, and deletion.
    """
    def __init__(
        self,
        store: Optional[BaseMemoryStore] = None,
        max_active_memories: int = MAX_ACTIVE_MEMORIES,
        default_limit: Optional[int] = None,
    ):
        self.store = store or InMemoryStore()
        self.max_active_memories = default_limit if default_limit is not None else max_active_memories

    def save_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "preference",
        importance: int = 3,
    ) -> MemoryRecord:
        """
        Creates/updates and stores a memory record for a specific user.
        If a memory of the same type contains a conflicting preference, updates the existing record.
        """
        user_memories = self.store.get_by_user(user_id)
        content_lowered = content.lower().strip()

        # Simple conflict override: if user updates a preference (e.g. "prefers Java" -> "prefers Python")
        for existing in user_memories:
            if existing.memory_type == memory_type and "prefer" in content_lowered and "prefer" in existing.content.lower():
                existing.content = content.strip()
                existing.importance = importance
                existing.created_at = datetime.now(timezone.utc).isoformat()
                MemoryRepository.update_memory(existing.id, user_id, existing.content, existing.importance)
                return existing

        record = MemoryRecord(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
        )
        self.store.save(record)
        return record

    def get_relevant_memories(
        self,
        user_id: str,
        query: str = "",
        limit: Optional[int] = None,
        memory_type: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """
        Retrieves candidate memories, scores them based on relevance + importance + recency,
        and returns the top N ranked memories.
        """
        if not user_id:
            return []

        all_user_memories = self.store.get_by_user(user_id)
        if memory_type:
            all_user_memories = [m for m in all_user_memories if m.memory_type == memory_type]

        if not all_user_memories:
            return []

        total_count = len(all_user_memories)
        scored = []
        for idx, record in enumerate(reversed(all_user_memories)):
            s = score_memory_relevance(record, query, idx, total_count)
            scored.append((s, record))

        # Sort descending by relevance score
        scored.sort(key=lambda item: item[0], reverse=True)

        max_items = limit if limit is not None else self.max_active_memories
        return [record for _, record in scored[:max_items]]

    def get_memories(
        self,
        user_id: str,
        limit: Optional[int] = None,
        memory_type: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """
        Backward-compatible retrieval method aliased to get_relevant_memories.
        """
        return self.get_relevant_memories(user_id=user_id, query="", limit=limit, memory_type=memory_type)

    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """
        Deletes a specific memory belonging to user_id.
        """
        if not memory_id or not user_id:
            return False
        return self.store.delete(memory_id, user_id)

    def extract_and_save_if_relevant(self, user_id: str, text: str) -> Optional[MemoryRecord]:
        """
        Rule-based memory detection for explicit user statements (preferences, instructions, projects).
        """
        if not text or not user_id:
            return None

        lowered = text.lower().strip()

        patterns = [
            (r"(?:i prefer|i like)\s+(.+)", "preference", 4),
            (r"(?:my project is|i am building)\s+(.+)", "project", 4),
            (r"(?:remember that|note that)\s+(.+)", "instruction", 5),
            (r"(?:i use|my stack is)\s+(.+)", "preference", 3),
        ]

        for pattern, mem_type, default_imp in patterns:
            match = re.search(pattern, lowered)
            if match:
                extracted_content = f"User preference/fact: {match.group(0).strip()}"
                return self.save_memory(
                    user_id=user_id,
                    content=extracted_content,
                    memory_type=mem_type,
                    importance=default_imp,
                )
        return None

default_memory_manager = MemoryManager()
