"""
Payment router for manual UPI payment processing.
Handles payment request submission (user) and approval/rejection (admin).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.dependencies import get_current_user, verify_admin_key
from backend.models.db_models import User, PaymentRequest
from backend.services.payment_service import PaymentService


router = APIRouter(prefix="/payment", tags=["Payment"])


def get_screenshot_url(request: Request, screenshot_path: Optional[str]) -> Optional[str]:
    """Convert file path to full URL for accessing the screenshot."""
    if not screenshot_path:
        return None
    # screenshot_path is like "uploads/screenshots/filename.jpg"
    # Use configured public_base_url if set, otherwise fall back to request.base_url
    if settings.public_base_url:
        base_url = settings.public_base_url.rstrip("/")
    else:
        base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/{screenshot_path}"


# ===== Request/Response Models =====

class PaymentRequestCreate(BaseModel):
    """Request model for creating a payment request."""
    upi_transaction_id: Optional[str] = Field(
        None,
        description="Optional UPI transaction reference ID",
        max_length=100
    )


class PaymentRequestResponse(BaseModel):
    """Response model for a payment request."""
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    amount: float
    upi_transaction_id: Optional[str] = None
    screenshot_path: Optional[str] = None
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentRequestListResponse(BaseModel):
    """Response model for listing payment requests."""
    success: bool
    requests: List[PaymentRequestResponse]
    count: int


class PaymentSubmitResponse(BaseModel):
    """Response model for submitting a payment request."""
    success: bool
    message: str
    request_id: Optional[str] = None


class PaymentActionResponse(BaseModel):
    """Response model for admin actions on payment requests."""
    success: bool
    message: str
    user_email: Optional[str] = None


class PendingStatusResponse(BaseModel):
    """Response model for checking pending payment status."""
    has_pending: bool
    pending_request: Optional[PaymentRequestResponse] = None


class CreditsResponse(BaseModel):
    """Response model for credits balance."""
    credits: int
    has_credits: bool


# ===== User Endpoints =====

@router.post("/request", response_model=PaymentSubmitResponse)
async def submit_payment_request(
    screenshot: UploadFile = File(...),
    upi_transaction_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a payment request after making UPI payment.

    User should call this endpoint after they have transferred money
    via UPI (PhonePe/GPay) to confirm their payment.
    """
    payment_service = PaymentService(db)

    # Check if user already has a pending request
    if await payment_service.has_pending_request(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="You already have a pending payment request. Please wait for it to be processed."
        )

    # Save screenshot
    uploads_dir = Path("uploads/screenshots")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Sanitize filename
    sanitized_filename = "".join(c for c in Path(screenshot.filename).name if c.isalnum() or c in ('.', '_')).rstrip()
    filename = f"{current_user.id}_{timestamp}_{sanitized_filename}"
    filepath = uploads_dir / filename
    
    with open(filepath, "wb") as buffer:
        buffer.write(await screenshot.read())

    # Create payment request
    payment_request = await payment_service.create_payment_request(
        user_id=current_user.id,
        upi_transaction_id=upi_transaction_id,
        screenshot_path=str(filepath)
    )
    await db.commit()

    return PaymentSubmitResponse(
        success=True,
        message="Payment request submitted successfully. Your account will be activated within 24 hours.",
        request_id=str(payment_request.id)
    )


@router.get("/credits", response_model=CreditsResponse)
async def get_credits_balance(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's credit balance.
    """
    credits = current_user.credits or 0
    return CreditsResponse(
        credits=credits,
        has_credits=credits > 0
    )


@router.get("/status", response_model=PendingStatusResponse)
async def get_payment_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if current user has a pending payment request.
    """
    payment_service = PaymentService(db)
    requests = await payment_service.get_user_payment_requests(
        current_user.id,
        status="pending"
    )

    if requests:
        pending = requests[0]
        return PendingStatusResponse(
            has_pending=True,
            pending_request=PaymentRequestResponse(
                id=str(pending.id),
                user_id=str(pending.user_id),
                amount=float(pending.amount),
                upi_transaction_id=pending.upi_transaction_id,
                status=pending.status,
                created_at=pending.created_at,
                processed_at=pending.processed_at,
                processed_by=pending.processed_by,
                notes=pending.notes,
            )
        )

    return PendingStatusResponse(has_pending=False)


@router.get("/history", response_model=PaymentRequestListResponse)
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all payment requests for the current user.
    """
    payment_service = PaymentService(db)
    requests = await payment_service.get_user_payment_requests(current_user.id)

    return PaymentRequestListResponse(
        success=True,
        requests=[
            PaymentRequestResponse(
                id=str(r.id),
                user_id=str(r.user_id),
                amount=float(r.amount),
                upi_transaction_id=r.upi_transaction_id,
                status=r.status,
                created_at=r.created_at,
                processed_at=r.processed_at,
                processed_by=r.processed_by,
                notes=r.notes,
            )
            for r in requests
        ],
        count=len(requests)
    )


# ===== Admin Endpoints =====

@router.get("/requests", response_model=PaymentRequestListResponse)
async def list_payment_requests(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _admin: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    [Admin] List all payment requests.

    Requires X-Admin-Key header.
    """
    payment_service = PaymentService(db)
    requests = await payment_service.get_all_payment_requests(
        status=status,
        limit=limit,
        offset=offset,
    )

    # Get user details for each request
    response_items = []
    for r in requests:
        # Fetch user email
        user = await db.get(User, r.user_id)
        response_items.append(
            PaymentRequestResponse(
                id=str(r.id),
                user_id=str(r.user_id),
                user_email=user.email if user else None,
                user_name=user.full_name if user else None,
                amount=float(r.amount),
                upi_transaction_id=r.upi_transaction_id,
                screenshot_path=get_screenshot_url(request, r.screenshot_path),
                status=r.status,
                created_at=r.created_at,
                processed_at=r.processed_at,
                processed_by=r.processed_by,
                notes=r.notes,
            )
        )

    return PaymentRequestListResponse(
        success=True,
        requests=response_items,
        count=len(response_items)
    )


@router.post("/activate/{request_id}", response_model=PaymentActionResponse)
async def activate_payment_request(
    request_id: str,
    notes: Optional[str] = Query(None, description="Admin notes"),
    premium_days: int = Query(30, ge=1, le=365, description="Days of premium to grant"),
    _admin: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    [Admin] Approve a payment request and activate user's premium.

    Requires X-Admin-Key header.
    """
    try:
        request_uuid = UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")

    payment_service = PaymentService(db)
    payment_request = await payment_service.approve_payment_request(
        request_id=request_uuid,
        admin_identifier="admin",
        premium_days=premium_days,
        notes=notes,
    )

    if not payment_request:
        raise HTTPException(status_code=404, detail="Payment request not found")

    await db.commit()

    # Get user email and credits for response
    user = await db.get(User, payment_request.user_id)

    return PaymentActionResponse(
        success=True,
        message=f"Added 10 credits. User now has {user.credits if user else 10} credits.",
        user_email=user.email if user else None
    )


@router.post("/reject/{request_id}", response_model=PaymentActionResponse)
async def reject_payment_request(
    request_id: str,
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    _admin: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    [Admin] Reject a payment request.

    Requires X-Admin-Key header.
    """
    try:
        request_uuid = UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")

    payment_service = PaymentService(db)
    payment_request = await payment_service.reject_payment_request(
        request_id=request_uuid,
        admin_identifier="admin",
        reason=reason,
    )

    if not payment_request:
        raise HTTPException(status_code=404, detail="Payment request not found")

    await db.commit()

    # Get user email for response
    user = await db.get(User, payment_request.user_id)

    return PaymentActionResponse(
        success=True,
        message="Payment request rejected",
        user_email=user.email if user else None
    )


@router.get("/pending-count")
async def get_pending_count(
    _admin: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    [Admin] Get count of pending payment requests.

    Requires X-Admin-Key header.
    """
    payment_service = PaymentService(db)
    count = await payment_service.get_pending_count()
    return {"pending_count": count}
