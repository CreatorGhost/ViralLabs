"""
Payment service for manual UPI payment processing.
Handles payment request creation, approval, and rejection.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import PaymentRequest, User


class PaymentService:
    """Service class for manual payment operations."""

    # Default premium duration: 30 days
    DEFAULT_PREMIUM_DAYS = 30
    DEFAULT_AMOUNT = Decimal("50.00")
    # Credits per purchase (₹50 = 10 credits)
    CREDITS_PER_PURCHASE = 10

    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== User Operations =====

    async def create_payment_request(
        self,
        user_id: UUID,
        upi_transaction_id: Optional[str] = None,
        amount: Optional[Decimal] = None,
        screenshot_path: Optional[str] = None,
    ) -> PaymentRequest:
        """
        Create a new payment request after user makes UPI payment.

        Args:
            user_id: The user's UUID
            upi_transaction_id: Optional UPI transaction reference
            amount: Payment amount (defaults to 50.00)
            screenshot_path: Path to the uploaded payment screenshot

        Returns:
            Created PaymentRequest object
        """
        payment_request = PaymentRequest(
            user_id=user_id,
            amount=amount or self.DEFAULT_AMOUNT,
            upi_transaction_id=upi_transaction_id,
            status="pending",
            screenshot_path=screenshot_path,
        )
        self.db.add(payment_request)
        await self.db.flush()
        return payment_request

    async def get_user_payment_requests(
        self,
        user_id: UUID,
        status: Optional[str] = None,
    ) -> List[PaymentRequest]:
        """Get all payment requests for a user, optionally filtered by status."""
        query = select(PaymentRequest).where(PaymentRequest.user_id == user_id)
        if status:
            query = query.where(PaymentRequest.status == status)
        query = query.order_by(PaymentRequest.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def has_pending_request(self, user_id: UUID) -> bool:
        """Check if user has a pending payment request."""
        result = await self.db.execute(
            select(PaymentRequest).where(
                PaymentRequest.user_id == user_id,
                PaymentRequest.status == "pending"
            )
        )
        return result.scalar_one_or_none() is not None

    # ===== Admin Operations =====

    async def get_all_payment_requests(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PaymentRequest]:
        """
        Get all payment requests for admin view.

        Args:
            status: Filter by status (pending, approved, rejected)
            limit: Maximum number of results
            offset: Pagination offset
        """
        query = select(PaymentRequest)
        if status:
            query = query.where(PaymentRequest.status == status)
        query = query.order_by(PaymentRequest.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_payment_request_by_id(
        self,
        request_id: UUID,
    ) -> Optional[PaymentRequest]:
        """Get a specific payment request by ID."""
        result = await self.db.execute(
            select(PaymentRequest).where(PaymentRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def approve_payment_request(
        self,
        request_id: UUID,
        admin_identifier: str = "admin",
        premium_days: int = DEFAULT_PREMIUM_DAYS,
        notes: Optional[str] = None,
    ) -> Optional[PaymentRequest]:
        """
        Approve a payment request and activate user's premium status.

        Args:
            request_id: The payment request UUID
            admin_identifier: Who processed this request
            premium_days: Number of days to grant premium access
            notes: Optional admin notes

        Returns:
            Updated PaymentRequest or None if not found
        """
        payment_request = await self.get_payment_request_by_id(request_id)
        if not payment_request:
            return None

        if payment_request.status != "pending":
            return payment_request  # Already processed

        # Update payment request
        payment_request.status = "approved"
        payment_request.processed_at = datetime.now(timezone.utc)
        payment_request.processed_by = admin_identifier
        if notes:
            payment_request.notes = notes

        # Update user's credits (add 10 credits per purchase, stackable)
        user_result = await self.db.execute(
            select(User).where(User.id == payment_request.user_id)
        )
        user = user_result.scalar_one_or_none()

        if user:
            # Add credits (stackable on repeat purchases)
            user.credits = (user.credits or 0) + self.CREDITS_PER_PURCHASE
            # Keep is_premium in sync with credits for backward compatibility
            user.is_premium = user.credits > 0
            user.updated_at = datetime.now(timezone.utc)

        return payment_request

    async def reject_payment_request(
        self,
        request_id: UUID,
        admin_identifier: str = "admin",
        reason: Optional[str] = None,
    ) -> Optional[PaymentRequest]:
        """
        Reject a payment request.

        Args:
            request_id: The payment request UUID
            admin_identifier: Who processed this request
            reason: Reason for rejection

        Returns:
            Updated PaymentRequest or None if not found
        """
        payment_request = await self.get_payment_request_by_id(request_id)
        if not payment_request:
            return None

        if payment_request.status != "pending":
            return payment_request  # Already processed

        payment_request.status = "rejected"
        payment_request.processed_at = datetime.now(timezone.utc)
        payment_request.processed_by = admin_identifier
        payment_request.notes = reason

        return payment_request

    async def get_pending_count(self) -> int:
        """Get count of pending payment requests."""
        result = await self.db.execute(
            select(PaymentRequest).where(PaymentRequest.status == "pending")
        )
        return len(list(result.scalars().all()))
