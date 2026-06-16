import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime,
    ForeignKey, Enum, Text, BigInteger, Float, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PlanName(str, enum.Enum):
    free = "free"
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    past_due = "past_due"
    trialing = "trialing"
    expired = "expired"


class PaymentGateway(str, enum.Enum):
    stripe = "stripe"
    razorpay = "razorpay"
    cashfree = "cashfree"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class TextStyle(str, enum.Enum):
    formal = "formal"
    casual = "casual"
    technical = "technical"
    simple = "simple"


# ---------------------------------------------------------------------------
# Plan (static catalogue, seeded at startup)
# ---------------------------------------------------------------------------

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlanName), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    price_inr = Column(Float, nullable=False, default=0)   # monthly price ₹
    price_usd = Column(Float, nullable=False, default=0)   # monthly price $
    requests_per_day = Column(Integer, nullable=False)      # -1 = unlimited
    max_chars_per_request = Column(Integer, nullable=False)
    features = Column(JSON, nullable=False, default=list)   # list of feature keys

    # Gateway plan IDs (set after creating products in each gateway dashboard)
    stripe_price_id = Column(String(200), nullable=True)
    razorpay_plan_id = Column(String(200), nullable=True)
    cashfree_plan_id = Column(String(200), nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Gateway customer IDs
    stripe_customer_id = Column(String(200), nullable=True)
    razorpay_customer_id = Column(String(200), nullable=True)
    cashfree_customer_id = Column(String(200), nullable=True)

    subscriptions = relationship("Subscription", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")
    transactions = relationship("PaymentTransaction", back_populates="user")


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.trialing)
    gateway = Column(Enum(PaymentGateway), nullable=True)

    # Gateway-side subscription/order IDs
    gateway_subscription_id = Column(String(300), nullable=True, index=True)
    gateway_customer_id = Column(String(300), nullable=True)

    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    transactions = relationship("PaymentTransaction", back_populates="subscription")


# ---------------------------------------------------------------------------
# API Key
# ---------------------------------------------------------------------------

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, default="default")
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="api_keys")


# ---------------------------------------------------------------------------
# Usage Log
# ---------------------------------------------------------------------------

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    endpoint = Column(String(200), nullable=False)
    chars_processed = Column(Integer, default=0)
    operations = Column(JSON, default=list)   # list of cleaning ops applied
    response_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="usage_logs")


# ---------------------------------------------------------------------------
# Payment Transaction
# ---------------------------------------------------------------------------

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    gateway = Column(Enum(PaymentGateway), nullable=False)
    gateway_payment_id = Column(String(300), nullable=True, index=True)
    gateway_order_id = Column(String(300), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transactions")
