"""Authentication endpoints: register, login."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user,
)
from app.database import get_db
from app.models.base import User, Plan, Subscription, SubscriptionStatus, PlanName
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=dict)
async def register(req: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with free tier."""
    # Check if user exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
    )
    db.add(user)
    db.flush()

    # Auto-subscribe to free plan
    free_plan = db.query(Plan).filter(Plan.name == PlanName.free).first()
    if not free_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Free plan not configured",
        )

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=user.id,
        plan_id=free_plan.id,
        status=SubscriptionStatus.active,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    db.add(subscription)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "user_id": str(user.id),
        "email": user.email,
    }


@router.post("/login", response_model=Token)
async def login(req: UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account disabled"
        )

    access_token = create_access_token(subject=str(user.id))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return user
