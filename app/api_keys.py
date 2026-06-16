"""API key generation, hashing, and FastAPI dependency."""
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.base import APIKey, User

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
_KEY_PREFIX = "atc_"  # ai-text-cleaning


def generate_api_key() -> str:
    """Return a plain-text API key. Store only the hash."""
    return _KEY_PREFIX + secrets.token_urlsafe(32)


def hash_api_key(plain_key: str) -> str:
    return hashlib.sha256(plain_key.encode()).hexdigest()


def get_user_by_api_key(
    api_key: Optional[str] = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Resolve an API key to its owner. Returns None if header absent."""
    if not api_key:
        return None
    key_hash = hash_api_key(api_key)
    record = (
        db.query(APIKey)
        .filter(APIKey.key_hash == key_hash, APIKey.is_active == True)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    # update last_used_at
    record.last_used_at = datetime.now(timezone.utc)
    db.commit()
    user = db.query(User).filter(User.id == record.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
