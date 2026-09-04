import pytest
from orchestrator.context import ContextManager, ConversationContext, default_context_manager

def test_context_manager_message_bounds_and_summarization():
    mgr = ContextManager(max_recent=3)
    session_id = "session-test-ctx"
    user_id = "user-ctx-1"

    # Create 5 messages
    messages = [
        {"role": "user", "content": f"Message {i}"} for i in range(1, 6)
    ]

    ctx = mgr.update_context(session_id=session_id, user_id=user_id, messages=messages)
    assert len(ctx.recent_messages) == 3
    assert ctx.recent_messages[0]["content"] == "Message 3"
    assert ctx.recent_messages[-1]["content"] == "Message 5"

    # Verify older messages were summarized
    assert ctx.conversation_summary is not None
    assert "Message 1" in ctx.conversation_summary
    assert "Message 2" in ctx.conversation_summary

def test_context_reference_resolution():
    mgr = ContextManager()
    session_id = "session-ref-1"
    user_id = "user-ref-1"

    messages = [
        {"role": "user", "content": "I am working on project Apollo."}
    ]
    ctx = mgr.update_context(session_id=session_id, user_id=user_id, messages=messages)

    resolved = mgr.resolve_references("How is that project doing?", ctx)
    assert "project Apollo" in resolved or "Apollo" in resolved

def test_context_user_isolation():
    mgr = ContextManager()
    mgr.update_context(session_id="s1", user_id="userA", messages=[{"role": "user", "content": "Hello"}])

    with pytest.raises(PermissionError, match="Session belongs to another user"):
        mgr.update_context(session_id="s1", user_id="userB", messages=[{"role": "user", "content": "Hijack"}])

def test_context_priority_system_prompt_builder():
    mgr = ContextManager()
    ctx = ConversationContext(
        session_id="s2",
        user_id="u2",
        active_task="Research AI trends",
        conversation_summary="Prior discussion on Machine Learning.",
    )

    prompt = mgr.build_llm_system_prompt(
        base_system_prompt="You are Jarvis.",
        context=ctx,
        profile_items=["Prefers Python"],
        memory_items=["Working on Django blog"],
    )

    assert "You are Jarvis." in prompt
    assert "--- ACTIVE TASK ---" in prompt
    assert "Research AI trends" in prompt
    assert "--- PRIOR CONVERSATION SUMMARY ---" in prompt
    assert "--- USER PROFILE ---" in prompt
    assert "--- LONG-TERM MEMORY ---" in prompt
