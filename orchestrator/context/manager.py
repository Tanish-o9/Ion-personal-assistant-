import time
import re
from typing import Any, Dict, List, Optional
from orchestrator.context.models import ConversationContext
from orchestrator.cache import default_cache, make_cache_key
from orchestrator.observability import jarvis_logger

MAX_RECENT_MESSAGES = 6
MAX_SUMMARY_LENGTH = 500

class ContextManager:
    """
    Intelligent conversation context manager supporting bounded context windows,
    older message summarization, reference resolution, and priority context construction.
    """
    def __init__(self, max_recent: int = MAX_RECENT_MESSAGES):
        self.max_recent = max_recent
        self._contexts: Dict[str, ConversationContext] = {}

    def get_or_create_context(self, session_id: str, user_id: str) -> ConversationContext:
        if session_id not in self._contexts:
            ctx = ConversationContext(session_id=session_id, user_id=user_id, last_updated=time.time())
            self._contexts[session_id] = ctx
        return self._contexts[session_id]

    def resolve_references(self, text: str, context: ConversationContext) -> str:
        """
        Resolves ambiguous pronouns ("that project", "the previous one", "same thing") using active entities.
        """
        if not text or not context.active_entities:
            return text

        resolved = text
        for ref_word, actual_entity in context.active_entities.items():
            pattern = re.compile(r"\b" + re.escape(ref_word) + r"\b", re.IGNORECASE)
            if pattern.search(resolved):
                resolved = pattern.sub(f"{actual_entity} ({ref_word})", resolved)
        return resolved

    def update_context(
        self,
        session_id: str,
        user_id: str,
        messages: List[Dict[str, Any]],
        active_task: Optional[str] = None,
    ) -> ConversationContext:
        ctx = self.get_or_create_context(session_id, user_id)
        if ctx.user_id != user_id:
            raise PermissionError("User isolation error: Session belongs to another user.")

        if active_task:
            ctx.active_task = active_task

        # Extract entities from recent messages
        for msg in messages[-3:]:
            content = msg.get("content", "")
            if "project" in content.lower():
                match = re.search(r"project\s+([A-Za-z0-9_\-]+)", content, re.IGNORECASE)
                if match:
                    ctx.active_entities["that project"] = match.group(0)

        # Truncate and summarize if message count exceeds max_recent
        if len(messages) > self.max_recent:
            older = messages[:-self.max_recent]
            recent = messages[-self.max_recent:]
            ctx.recent_messages = recent

            # Construct concise summary of older messages
            summary_parts = []
            for m in older:
                role = m.get("role", "user")
                c = m.get("content", "")[:100]
                summary_parts.append(f"{role.capitalize()}: {c}")

            ctx.conversation_summary = "Prior Conversation Summary:\n" + "\n".join(summary_parts[:6])
            if len(ctx.conversation_summary) > MAX_SUMMARY_LENGTH:
                ctx.conversation_summary = ctx.conversation_summary[:MAX_SUMMARY_LENGTH] + "..."
        else:
            ctx.recent_messages = messages
            ctx.conversation_summary = None

        ctx.last_updated = time.time()
        ctx.estimated_tokens = sum(len(m.get("content", "").split()) for m in ctx.recent_messages)

        # User-scoped context caching
        cache_key = make_cache_key("context", user_id, session_id)
        default_cache.set(cache_key, ctx.to_dict(), ttl_seconds=600)

        return ctx

    def build_llm_system_prompt(
        self,
        base_system_prompt: str,
        context: ConversationContext,
        profile_items: Optional[List[str]] = None,
        memory_items: Optional[List[str]] = None,
    ) -> str:
        """
        Builds system prompt applying strict priority:
        1. Base System Instructions
        2. Active Task / Plan
        3. Older Conversation Summary
        4. User Profile
        5. Long-term Memory
        """
        sections = [base_system_prompt]

        if context.active_task:
            sections.append(f"\n--- ACTIVE TASK ---\n{context.active_task}")

        if context.conversation_summary:
            sections.append(f"\n--- PRIOR CONVERSATION SUMMARY ---\n{context.conversation_summary}")

        if profile_items:
            prof_text = "\n".join([f"- {p}" for p in profile_items])
            sections.append(f"\n--- USER PROFILE ---\n{prof_text}")

        if memory_items:
            mem_text = "\n".join([f"- {m}" for m in memory_items])
            sections.append(f"\n--- LONG-TERM MEMORY ---\n{mem_text}")

        return "\n".join(sections)

default_context_manager = ContextManager()
