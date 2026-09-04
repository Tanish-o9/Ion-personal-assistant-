import hashlib
import uuid
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class APIKeyModel(BaseModel):
    key_id: str
    user_id: str
    key_hash: str
    scopes: List[str] = Field(default_factory=list)
    revoked: bool = False

class APIKeyManager:
    """
    Manages hashed API key generation, scope checks, and key revocation.
    """
    def __init__(self):
        self.keys: Dict[str, APIKeyModel] = {}

    def create_api_key(self, user_id: str, scopes: List[str]) -> Tuple[str, APIKeyModel]:
        raw_key = f"jrv_{uuid.uuid4().hex}"
        key_id = str(uuid.uuid4())
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        key_model = APIKeyModel(
            key_id=key_id,
            user_id=user_id,
            key_hash=key_hash,
            scopes=scopes,
        )
        self.keys[raw_key] = key_model
        return raw_key, key_model

    def validate_key(self, raw_key: str, required_scope: str) -> Optional[APIKeyModel]:
        key_model = self.keys.get(raw_key)
        if not key_model or key_model.revoked:
            return None
        if required_scope not in key_model.scopes and "*" not in key_model.scopes:
            return None
        return key_model

default_api_key_manager = APIKeyManager()
