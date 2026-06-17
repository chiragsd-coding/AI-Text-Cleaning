"""
Pydantic schemas for request/response validation.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ============================================================================
# Authentication & User
# ============================================================================


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Text Cleaning
# ============================================================================


class TextCleanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    operations: Optional[List[str]] = Field(
        default=None,
        description="List of operations to apply. If null, applies all. Valid: grammar, spaces, capitalization, emojis, profanity, pii, ocr, style",
    )
    target_style: Optional[str] = Field(
        default="formal",
        description="Target text style: formal, casual, technical, simple",
    )


class OperationMetadata(BaseModel):
    grammar: Optional[Dict[str, Any]] = None
    spaces: Optional[Dict[str, Any]] = None
    capitalization: Optional[Dict[str, Any]] = None
    emojis: Optional[Dict[str, Any]] = None
    profanity: Optional[Dict[str, Any]] = None
    pii: Optional[Dict[str, Any]] = None
    ocr: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None


class TextCleanResponse(BaseModel):
    original_text: str
    cleaned_text: str
    operations_applied: List[str]
    metadata: Dict[str, Any]


class BulkTextCleanRequest(BaseModel):
    texts: List[str] = Field(..., max_items=1000)
    operations: Optional[List[str]] = None
    target_style: Optional[str] = "formal"


class BulkTextCleanResponse(BaseModel):
    results: List[TextCleanResponse]
    total_processed: int
    total_chars_processed: int


# ============================================================================
# API Key Management
# ============================================================================


class APIKeyCreate(BaseModel):
    name: Optional[str] = Field(default="API Key")


class APIKeyResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyFullResponse(APIKeyResponse):
    key: str  # Only returned on creation


# ============================================================================
# Subscription & Plans
# ============================================================================


class PlanResponse(BaseModel):

    id: UUID
    name: str
    display_name: str
    price_inr: float
    price_usd: float
    requests_per_day: int
    max_chars_per_request: int
    features: List[str]

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpgradeRequest(BaseModel):
    plan_name: str = Field(..., description="Plan name: free, starter, pro, enterprise")
    gateway: str = Field(..., description="Payment gateway: stripe, razorpay, cashfree")


# ============================================================================
# Payments
# ============================================================================


class PaymentInitiateRequest(BaseModel):
    subscription_id: Optional[str] = None
    plan_name: Optional[str] = None  # If no subscription, start new one
    gateway: str = Field(..., description="stripe, razorpay, or cashfree")
    return_url: Optional[str] = None


class PaymentWebhookStripe(BaseModel):
    type: str
    data: Dict[str, Any]


class PaymentWebhookRazorpay(BaseModel):
    event: str
    payload: Dict[str, Any]


class PaymentWebhookCashfree(BaseModel):
    type: str
    data: Dict[str, Any]


class PaymentStatusResponse(BaseModel):
    payment_id: str
    status: str
    gateway: str
    amount: float
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Usage & Analytics
# ============================================================================


class UsageStatsResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    chars_processed: int
    requests_made: int
    requests_limit: int
    chars_limit: int


class UsageLogResponse(BaseModel):
    id: UUID
    endpoint: str
    chars_processed: int
    operations: List[str]
    response_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Error Responses
# ============================================================================


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    error: str
    details: List[Dict[str, Any]]
    status_code: int = 422


# ============================================================================
# Health Check
# ============================================================================


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    timestamp: datetime
