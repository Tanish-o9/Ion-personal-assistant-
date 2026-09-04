import os
import json
import logging
from typing import Dict, Optional
from orchestrator.auth.models import User
from database.repository import UserRepository

logger = logging.getLogger(__name__)

class UserStore:
    """
    Persistent store for User accounts backed by database repository.
    """
    def register_user(self, username: str, password_hash: str) -> User:
        lowered_name = username.strip().lower()
        db_user = UserRepository.update_password(username=lowered_name, password_hash=password_hash)
        return User(id=db_user.id, username=db_user.username, password_hash=db_user.password_hash, created_at=db_user.created_at)

    def get_by_id(self, user_id: str) -> Optional[User]:
        db_user = UserRepository.get_by_id(user_id)
        if not db_user:
            return None
        return User(id=db_user.id, username=db_user.username, password_hash=db_user.password_hash, created_at=db_user.created_at)

    def get_by_username(self, username: str) -> Optional[User]:
        db_user = UserRepository.get_by_username(username)
        if not db_user:
            return None
        return User(id=db_user.id, username=db_user.username, password_hash=db_user.password_hash, created_at=db_user.created_at)

class SessionStore:
    """
    Tracks session_id to user_id ownership to enforce multi-user session isolation.
    """
    def __init__(self):
        self._session_owners: Dict[str, str] = {}

    def bind_session(self, session_id: str, user_id: str) -> None:
        """
        Binds a session_id to a specific user_id owner.
        """
        if session_id and user_id:
            self._session_owners[session_id] = user_id

    def get_owner(self, session_id: str) -> Optional[str]:
        """
        Returns the user_id owner of a session_id if bound.
        """
        return self._session_owners.get(session_id)

    def verify_ownership(self, session_id: str, user_id: str) -> bool:
        """
        Verifies if user_id owns session_id. If unassigned, binds ownership to user_id.
        """
        owner = self.get_owner(session_id)
        if owner is None:
            self.bind_session(session_id, user_id)
            return True
        return owner == user_id
