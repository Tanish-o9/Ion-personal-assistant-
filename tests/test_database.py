import pytest
from database import (
    init_db,
    UserRepository,
    ConversationRepository,
    MemoryRepository,
)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

# ---------------------------------------------------------------------------
# 1. User Database Persistence Tests
# ---------------------------------------------------------------------------

def test_user_repository_create_and_retrieve():
    user = UserRepository.create_user(username="db_user_1", password_hash="hash_123")
    assert user.id is not None
    assert user.username == "db_user_1"

    retrieved = UserRepository.get_by_id(user.id)
    assert retrieved is not None
    assert retrieved.username == "db_user_1"

    by_name = UserRepository.get_by_username("db_user_1")
    assert by_name is not None
    assert by_name.id == user.id

# ---------------------------------------------------------------------------
# 2. Conversation & Message Persistence Tests
# ---------------------------------------------------------------------------

def test_conversation_and_message_repository_persistence():
    user = UserRepository.create_user(username="db_user_conv", password_hash="hash_123")
    session_id = "session-db-test-1"

    conv = ConversationRepository.create_or_get_conversation(session_id=session_id, user_id=user.id, title="Test Chat")
    assert conv.session_id == session_id
    assert conv.user_id == user.id

    msg1 = ConversationRepository.save_message(session_id=session_id, role="user", content="Hello JARVIS")
    msg2 = ConversationRepository.save_message(session_id=session_id, role="assistant", content="Hello User")

    messages = ConversationRepository.get_session_messages(session_id)
    assert len(messages) == 2
    assert messages[0].content == "Hello JARVIS"
    assert messages[1].content == "Hello User"

    user_convs = ConversationRepository.get_user_conversations(user.id)
    assert len(user_convs) >= 1
    assert user_convs[0].session_id == session_id

# ---------------------------------------------------------------------------
# 3. Memory Repository Persistence & User Isolation
# ---------------------------------------------------------------------------

def test_memory_repository_user_isolation():
    u_a = UserRepository.create_user(username="mem_user_a", password_hash="hash_a")
    u_b = UserRepository.create_user(username="mem_user_b", password_hash="hash_b")

    m_a = MemoryRepository.save_memory(user_id=u_a.id, content="User A prefers Python", memory_type="preference", importance=5)
    m_b = MemoryRepository.save_memory(user_id=u_b.id, content="User B prefers Java", memory_type="preference", importance=4)

    mems_a = MemoryRepository.get_user_memories(u_a.id)
    mems_b = MemoryRepository.get_user_memories(u_b.id)

    assert len(mems_a) == 1
    assert mems_a[0].content == "User A prefers Python"

    assert len(mems_b) == 1
    assert mems_b[0].content == "User B prefers Java"

    # Delete memory test
    del_res = MemoryRepository.delete_memory(m_a.id, u_a.id)
    assert del_res is True
    assert len(MemoryRepository.get_user_memories(u_a.id)) == 0
