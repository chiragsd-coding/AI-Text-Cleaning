"""API key management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.base import User, APIKey
from app.api_keys import generate_api_key, hash_api_key
from app.schemas import APIKeyCreate, APIKeyResponse, APIKeyFullResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List all API keys for current user (does not return full key)."""
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    return keys


@router.post("", response_model=APIKeyFullResponse)
async def create_api_key(
    req: APIKeyCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new API key for current user.
    **IMPORTANT**: The key is only returned once. Store it securely.
    """
    plain_key = generate_api_key()

    key_hash = hash_api_key(plain_key)

    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        name=req.name or "API Key",
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeyFullResponse(
        id=str(api_key.id),
        name=api_key.name,
        key=plain_key,  # Only returned on creation!
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
    )


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    req: APIKeyCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update API key details (name, active status)."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    api_key.name = req.name or api_key.name
    db.commit()
    db.refresh(api_key)

    return api_key


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an API key (cannot be recovered)."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    db.delete(api_key)
    db.commit()

    return {"message": "API key deleted successfully"}


@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke an API key (mark as inactive) without deleting it."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    api_key.is_active = False
    db.commit()
    db.refresh(api_key)

    return {"message": "API key revoked successfully"}


@router.post("/{key_id}/activate")
async def activate_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Activate a revoked API key."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    api_key.is_active = True
    db.commit()
    db.refresh(api_key)

    return {"message": "API key activated successfully"}
