"""Subscription and plan management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.auth import get_current_user
from app.database import get_db
from app.models.base import User, Plan, Subscription, SubscriptionStatus, PlanName
from app.schemas import (
    PlanResponse,
    SubscriptionResponse,
    SubscriptionUpgradeRequest,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(db: Session = Depends(get_db)):
    """List all available subscription plans."""
    plans = db.query(Plan).all()

    return [PlanResponse.model_validate(p) for p in plans]


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's active subscription."""

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.active,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )

    return subscription


@router.post("/upgrade")
async def upgrade_subscription(
    req: SubscriptionUpgradeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upgrade or change subscription plan.
    Returns payment gateway initiation details.
    """
    # Get target plan
    plan = db.query(Plan).filter(Plan.name == PlanName[req.plan_name]).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
        )

    # Get current subscription
    current_sub = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.active,
        )
        .first()
    )

    # Cancel old subscription if upgrading
    if current_sub and current_sub.plan_id != plan.id:
        current_sub.status = SubscriptionStatus.cancelled
        current_sub.cancelled_at = datetime.now(timezone.utc)

    # Create new subscription
    now = datetime.now(timezone.utc)
    new_sub = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status=SubscriptionStatus.trialing,  # Until payment succeeds
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        gateway=PlanName[req.gateway],
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    # TODO: Integrate with payment gateway (stripe, razorpay, cashfree)
    # For now, return payment initiation data

    return {
        "subscription_id": str(new_sub.id),
        "plan_name": req.plan_name,
        "gateway": req.gateway,
        "amount": plan.price_usd,
        "currency": "USD",
        "message": "Payment gateway initiation needed. See payment_url.",
        # In real implementation, generate payment link for each gateway
    }


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Cancel current subscription."""
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.active,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription to cancel",
        )

    subscription.status = SubscriptionStatus.cancelled
    subscription.cancelled_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Subscription cancelled successfully"}
