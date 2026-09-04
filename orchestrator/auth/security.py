import os
import time
import hmac
import hashlib
import secrets
import base64
import json
from typing import Any, Dict, Optional

SECRET_KEY = os.getenv("SECRET_KEY", "jarvis_super_secret_jwt_key_2026").encode("utf-8")
SALT_SIZE = 16
HASH_ITERATIONS = 100000

def hash_password(password: str) -> str:
    """
    Hashes password using PBKDF2-HMAC-SHA256 with salt.
    Format: salt_hex:hash_hex
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_bytes(SALT_SIZE)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies a plain password against salt_hex:hash_hex PBKDF2 hash.
    """
    if not password or not password_hash or ":" not in password_hash:
        return False
    try:
        salt_hex, hash_hex = password_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
        return hmac.compare_digest(key.hex(), hash_hex)
    except Exception:
        return False

def create_token(user_id: str, username: str, expires_in_seconds: int = 2592000) -> str:
    """
    Generates a secure HMAC-SHA256 signed Bearer token containing user payload and long-lived expiration timestamp (30 days default).
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + expires_in_seconds,
    }
    json_bytes = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(json_bytes).decode("ascii").rstrip("=")

    signature = hmac.new(SECRET_KEY, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies token signature and expiration. Returns decoded user payload if valid.
    """
    if not token or "." not in token:
        return None

    try:
        payload_b64, signature = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return None

        # Re-pad base64 string
        rem = len(payload_b64) % 4
        if rem > 0:
            payload_b64 += "=" * (4 - rem)

        json_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(json_bytes.decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None
