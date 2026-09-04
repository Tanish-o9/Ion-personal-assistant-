import pytest
from fastapi.testclient import TestClient
from api.main import app
from orchestrator.auth import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
    default_user_store,
    default_session_store,
)

# ---------------------------------------------------------------------------
# 1. Security Unit Tests (PBKDF2 & HMAC-SHA256 Tokens)
# ---------------------------------------------------------------------------

def test_password_hashing_and_verification():
    raw_password = "SecretPassword123!"
    hashed = hash_password(raw_password)

    assert ":" in hashed
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_token_creation_and_verification():
    token = create_token(user_id="user-123", username="alice", expires_in_seconds=60)
    assert "." in token

    payload = verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "user-123"
    assert payload["username"] == "alice"

    # Expired or tampered token test
    tampered_token = token[:-5] + "x" * 5
    assert verify_token(tampered_token) is None

# ---------------------------------------------------------------------------
# 2. Registration & Login API Tests
# ---------------------------------------------------------------------------

def test_register_and_login_flow():
    client = TestClient(app)

    # 1. Register User A
    res_reg = client.post("/auth/register", json={"username": "alice", "password": "alicepassword"})
    assert res_reg.status_code == 200
    data_reg = res_reg.json()
    assert "token" in data_reg
    assert data_reg["user"]["username"] == "alice"

    # 2. Duplicate registration error
    res_dup = client.post("/auth/register", json={"username": "alice", "password": "anotherpassword"})
    assert res_dup.status_code == 400
    assert "Invalid registration data" in res_dup.json()["detail"]

    # 3. Login User A (valid credentials)
    res_login = client.post("/auth/login", json={"username": "alice", "password": "alicepassword"})
    assert res_login.status_code == 200
    assert "token" in res_login.json()

    # 4. Login User A (invalid credentials)
    res_bad = client.post("/auth/login", json={"username": "alice", "password": "wrongpassword"})
    assert res_bad.status_code == 401

# ---------------------------------------------------------------------------
# 3. Authorization & Multi-User Isolation Tests
# ---------------------------------------------------------------------------

def test_multi_user_isolation_and_protection():
    client = TestClient(app)

    # Register User A & User B
    reg_a = client.post("/auth/register", json={"username": "user_a", "password": "pass_a"}).json()
    reg_b = client.post("/auth/register", json={"username": "user_b", "password": "pass_b"}).json()

    token_a = reg_a["token"]
    user_a_id = reg_a["user"]["id"]

    token_b = reg_b["token"]
    user_b_id = reg_b["user"]["id"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Unauthenticated requests rejected with 401
    res_unauth = client.post("/chat", json={"text": "Hello"})
    assert res_unauth.status_code == 401

    # 2. Authenticated GET /memory for own user succeeds
    res_mem_a = client.get(f"/memory/{user_a_id}", headers=headers_a)
    assert res_mem_a.status_code == 200

    # 3. User A accessing User B's memories returns 403 Forbidden
    res_mem_cross = client.get(f"/memory/{user_b_id}", headers=headers_a)
    assert res_mem_cross.status_code == 403

    # 4. User A accessing User B's profile returns 403 Forbidden
    res_prof_cross = client.get(f"/profile/{user_b_id}", headers=headers_a)
    assert res_prof_cross.status_code == 403

    # 5. User A creates session A
    session_a = "session-owner-a"
    res_chat_a = client.post("/chat", json={"session_id": session_a, "text": "I am User A"}, headers=headers_a)
    assert res_chat_a.status_code == 200

    # 6. User B attempting to post to User A's session returns 403 Forbidden
    res_chat_b_hijack = client.post("/chat", json={"session_id": session_a, "text": "Hijacking session A"}, headers=headers_b)
    assert res_chat_b_hijack.status_code == 403
