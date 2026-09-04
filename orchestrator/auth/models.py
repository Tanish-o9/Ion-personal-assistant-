import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class User:
    """
    Represents an authenticated user identity in JARVIS.
    """
    def __init__(
        self,
        username: str,
        password_hash: str,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        if not username or not isinstance(username, str):
            raise ValueError("username must be a non-empty string.")
        if not password_hash or not isinstance(password_hash, str):
            raise ValueError("password_hash must be a non-empty string.")

        self.id = id or str(uuid.uuid4())
        self.username = username.strip().lower()
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data.get("id"),
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=data.get("created_at"),
        )
