"""Text cleaning endpoints: clean, autocorrect, batch processing."""
import time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.services.cleaner import get_text_cleaner
from app.schemas import (
    TextCleanRequest,
    TextCleanResponse,
    BulkTextCleanRequest,
    BulkTextCleanResponse,
)
from app.models.base import User, UsageLog, Subscription, SubscriptionStatus
from app.auth import get_current_user
from app.api_keys import get_user_by_api_key
from app.database import get_db

router = APIRouter(prefix="/clean", tags=["text-cleaning"])


def get_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user),
    api_key_user: Optional[User] = Depends(get_user_by_api_key),
    db: Session = Depends(get_db),
) -> tuple[User, Session]:
    """Get authenticated user from either JWT or API key."""
    user = current_user or api_key_user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user, db


async def check_usage_quota(user: User, db: Session, chars_count: int):
    """Check if user has remaining quota for today."""
    # Get active subscription
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription. Please upgrade.",
        )

    plan = subscription.plan
    if plan.requests_per_day != -1:  # -1 means unlimited
        # TODO: Check daily request count from UsageLog
        pass

    if plan.max_chars_per_request < chars_count:
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail=f"Text exceeds max length of {plan.max_chars_per_request} chars for your plan",
        )


@router.post("/text", response_model=TextCleanResponse)
async def clean_text(
    req: TextCleanRequest,
    user_db: tuple = Depends(get_authenticated_user),
):
    """
    Clean and autocorrect text with selected operations.

    Operations available:
    - grammar: Fix common grammar mistakes
    - spaces: Remove extra spaces, fix spacing
    - capitalization: Standardize capitalization
    - emojis: Remove emojis
    - profanity: Censor profanity
    - pii: Anonymize PII (emails, phone, SSN, etc)
    - ocr: Correct OCR errors and encoding issues
    - style: Convert text to different writing style
    """
    user, db = user_db

    # Check quota
    await check_usage_quota(user, db, len(req.text))

    # Clean text
    start_time = time.time()
    cleaner = get_text_cleaner()
    result = cleaner.clean(req.text, req.operations, req.target_style)
    response_ms = int((time.time() - start_time) * 1000)

    # Log usage
    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/text",
        chars_processed=len(req.text),
        operations=result["operations_applied"],
        response_ms=response_ms,
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=result["operations_applied"],
        metadata=result["metadata"],
    )


@router.post("/autocorrect", response_model=TextCleanResponse)
async def autocorrect_text(
    req: TextCleanRequest,
    user_db: tuple = Depends(get_authenticated_user),
):
    """
    Autocorrect text with smart operation selection.
    Automatically selects the best cleaning operations.
    """
    user, db = user_db

    # Auto-select operations: always apply space, grammar, capitalization
    auto_ops = ["spaces", "grammar", "capitalization"]

    # Detect if there's profanity or PII (optional)
    # For now, skip by default but user can override
    if req.operations:
        auto_ops = req.operations

    req.operations = auto_ops

    # Check quota
    await check_usage_quota(user, db, len(req.text))

    # Clean
    start_time = time.time()
    cleaner = get_text_cleaner()
    result = cleaner.clean(req.text, auto_ops, req.target_style)
    response_ms = int((time.time() - start_time) * 1000)

    # Log usage
    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/autocorrect",
        chars_processed=len(req.text),
        operations=auto_ops,
        response_ms=response_ms,
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=auto_ops,
        metadata=result["metadata"],
    )


@router.post("/batch", response_model=BulkTextCleanResponse)
async def clean_batch(
    req: BulkTextCleanRequest,
    user_db: tuple = Depends(get_authenticated_user),
):
    """
    Clean multiple texts in batch (up to 1000).
    Useful for bulk processing resumes, job descriptions, etc.
    """
    user, db = user_db

    # Check quota for total chars
    total_chars = sum(len(text) for text in req.texts)
    await check_usage_quota(user, db, total_chars)

    # Clean all texts
    cleaner = get_text_cleaner()
    results = []
    start_time = time.time()

    for text in req.texts:
        result = cleaner.clean(text, req.operations, req.target_style)
        results.append(
            TextCleanResponse(
                original_text=result["original_text"],
                cleaned_text=result["cleaned_text"],
                operations_applied=result["operations_applied"],
                metadata=result["metadata"],
            )
        )

    response_ms = int((time.time() - start_time) * 1000)

    # Log usage
    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/batch",
        chars_processed=total_chars,
        operations=req.operations or ["all"],
        response_ms=response_ms,
    )
    db.add(log)
    db.commit()

    return BulkTextCleanResponse(
        results=results,
        total_processed=len(req.texts),
        total_chars_processed=total_chars,
    )


@router.post("/grammar", response_model=TextCleanResponse)
async def fix_grammar(
    text: str,
    user_db: tuple = Depends(get_authenticated_user),
):
    """Fix grammar errors in text."""
    user, db = user_db
    await check_usage_quota(user, db, len(text))

    cleaner = get_text_cleaner()
    result = cleaner.clean(text, ["grammar"])

    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/grammar",
        chars_processed=len(text),
        operations=["grammar"],
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=["grammar"],
        metadata=result["metadata"],
    )


@router.post("/remove-pii", response_model=TextCleanResponse)
async def remove_pii(
    text: str,
    user_db: tuple = Depends(get_authenticated_user),
):
    """Remove personally identifiable information from text."""
    user, db = user_db
    await check_usage_quota(user, db, len(text))

    cleaner = get_text_cleaner()
    result = cleaner.clean(text, ["pii"])

    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/remove-pii",
        chars_processed=len(text),
        operations=["pii"],
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=["pii"],
        metadata=result["metadata"],
    )


@router.post("/remove-profanity", response_model=TextCleanResponse)
async def remove_profanity(
    text: str,
    user_db: tuple = Depends(get_authenticated_user),
):
    """Remove or censor profanity from text."""
    user, db = user_db
    await check_usage_quota(user, db, len(text))

    cleaner = get_text_cleaner()
    result = cleaner.clean(text, ["profanity"])

    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/remove-profanity",
        chars_processed=len(text),
        operations=["profanity"],
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=["profanity"],
        metadata=result["metadata"],
    )


@router.post("/remove-emojis", response_model=TextCleanResponse)
async def remove_emojis(
    text: str,
    user_db: tuple = Depends(get_authenticated_user),
):
    """Remove emojis from text."""
    user, db = user_db
    await check_usage_quota(user, db, len(text))

    cleaner = get_text_cleaner()
    result = cleaner.clean(text, ["emojis"])

    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/remove-emojis",
        chars_processed=len(text),
        operations=["emojis"],
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=["emojis"],
        metadata=result["metadata"],
    )


@router.post("/fix-ocr", response_model=TextCleanResponse)
async def fix_ocr(
    text: str,
    user_db: tuple = Depends(get_authenticated_user),
):
    """Correct OCR (Optical Character Recognition) errors."""
    user, db = user_db
    await check_usage_quota(user, db, len(text))

    cleaner = get_text_cleaner()
    result = cleaner.clean(text, ["ocr"])

    log = UsageLog(
        user_id=user.id,
        endpoint="/clean/fix-ocr",
        chars_processed=len(text),
        operations=["ocr"],
    )
    db.add(log)
    db.commit()

    return TextCleanResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        operations_applied=["ocr"],
        metadata=result["metadata"],
    )
