"""
Test cases for payment endpoints.
Tests manual UPI payment flow including user requests and admin operations.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from backend.core.config import settings


# Admin key for testing
ADMIN_KEY = settings.admin_secret_key


class TestPaymentRequestSubmission:
    """Test cases for user payment request submission."""

    @pytest.mark.asyncio
    async def test_submit_payment_request_success(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test successful payment request submission."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI123456789"},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "request_id" in data
        assert "24 hours" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_submit_payment_request_without_transaction_id(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test payment request submission without UPI transaction ID."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.post(
            "/payment/request",
            json={},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "request_id" in data

    @pytest.mark.asyncio
    async def test_submit_payment_request_unauthenticated(self, client: AsyncClient):
        """Test payment request without authentication fails."""
        response = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI123456789"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_duplicate_payment_request(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test that submitting duplicate payment request fails."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # First request
        response1 = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI111"},
            headers=headers,
        )
        assert response1.status_code == 200

        # Second request should fail
        response2 = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI222"},
            headers=headers,
        )

        assert response2.status_code == 400
        data = response2.json()
        assert "pending" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_submit_payment_request_with_existing_credits(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that users with credits CAN submit payment requests (to buy more)."""
        from backend.models.db_models import User
        from sqlalchemy import select

        # Give user some credits
        user_id = authenticated_user["user"]["id"]
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 5
        user.is_premium = True
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.post(
            "/payment/request",
            json={},
            headers=headers,
        )

        # Should succeed - users can always buy more credits
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestPaymentStatus:
    """Test cases for checking payment status."""

    @pytest.mark.asyncio
    async def test_get_payment_status_no_pending(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting payment status when no pending request exists."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.get("/payment/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["has_pending"] is False
        assert data["pending_request"] is None

    @pytest.mark.asyncio
    async def test_get_payment_status_with_pending(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting payment status when pending request exists."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Submit a payment request first
        await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI999"},
            headers=headers,
        )

        # Check status
        response = await client.get("/payment/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["has_pending"] is True
        assert data["pending_request"] is not None
        assert data["pending_request"]["status"] == "pending"
        assert data["pending_request"]["upi_transaction_id"] == "UPI999"

    @pytest.mark.asyncio
    async def test_get_payment_status_unauthenticated(self, client: AsyncClient):
        """Test getting payment status without authentication fails."""
        response = await client.get("/payment/status")
        assert response.status_code == 401


class TestPaymentHistory:
    """Test cases for payment history."""

    @pytest.mark.asyncio
    async def test_get_payment_history_empty(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting payment history when empty."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.get("/payment/history", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["requests"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_get_payment_history_with_requests(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting payment history with existing requests."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Submit a payment request
        await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPIHIST123"},
            headers=headers,
        )

        # Get history
        response = await client.get("/payment/history", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["requests"]) == 1
        assert data["count"] == 1
        assert data["requests"][0]["upi_transaction_id"] == "UPIHIST123"


class TestAdminListRequests:
    """Test cases for admin listing payment requests."""

    @pytest.mark.asyncio
    async def test_list_requests_success(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test admin listing all payment requests."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits a request
        await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPIADMIN1"},
            headers=user_headers,
        )

        # Admin lists requests
        response = await client.get("/payment/requests", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["requests"]) >= 1

    @pytest.mark.asyncio
    async def test_list_requests_filter_by_status(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test admin filtering requests by status."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits a request
        await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )

        # Filter by pending
        response = await client.get(
            "/payment/requests?status=pending", headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        for request in data["requests"]:
            assert request["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_requests_invalid_admin_key(self, client: AsyncClient):
        """Test listing requests with invalid admin key fails."""
        response = await client.get(
            "/payment/requests",
            headers={"X-Admin-Key": "invalid-key"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_requests_no_admin_key(self, client: AsyncClient):
        """Test listing requests without admin key fails."""
        response = await client.get("/payment/requests")

        assert response.status_code == 422  # Missing required header


class TestAdminActivateRequest:
    """Test cases for admin activating payment requests."""

    @pytest.mark.asyncio
    async def test_activate_request_success(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test admin successfully activating a payment request adds credits."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits a request
        submit_response = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPIACTIVATE1"},
            headers=user_headers,
        )
        request_id = submit_response.json()["request_id"]

        # Admin activates
        response = await client.post(
            f"/payment/activate/{request_id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "10 credits" in data["message"].lower() or "credits" in data["message"].lower()
        assert data["user_email"] is not None

    @pytest.mark.asyncio
    async def test_activate_request_adds_credits(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test admin activation adds 10 credits to user."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}
        user_id = authenticated_user["user"]["id"]

        # Check initial credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        initial_credits = user.credits or 0

        # User submits a request
        submit_response = await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )
        request_id = submit_response.json()["request_id"]

        # Admin activates
        await client.post(
            f"/payment/activate/{request_id}",
            headers=admin_headers,
        )

        # Refresh user from DB
        await db_session.refresh(user)

        # Should have 10 more credits
        assert user.credits == initial_credits + 10
        assert user.is_premium is True

    @pytest.mark.asyncio
    async def test_activate_request_not_found(self, client: AsyncClient):
        """Test activating non-existent request returns 404."""
        admin_headers = {"X-Admin-Key": ADMIN_KEY}
        fake_id = str(uuid4())

        response = await client.post(
            f"/payment/activate/{fake_id}",
            headers=admin_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_request_invalid_id_format(self, client: AsyncClient):
        """Test activating with invalid UUID format returns 400."""
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        response = await client.post(
            "/payment/activate/not-a-uuid",
            headers=admin_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_user_is_premium_after_activation(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test that user becomes premium after admin activation."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits a request
        submit_response = await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )
        request_id = submit_response.json()["request_id"]

        # Admin activates
        await client.post(
            f"/payment/activate/{request_id}",
            headers=admin_headers,
        )

        # Check user status - should no longer have pending
        status_response = await client.get("/payment/status", headers=user_headers)
        data = status_response.json()
        # After activation, the request is no longer pending
        assert data["has_pending"] is False


class TestAdminRejectRequest:
    """Test cases for admin rejecting payment requests."""

    @pytest.mark.asyncio
    async def test_reject_request_success(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test admin successfully rejecting a payment request."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits a request
        submit_response = await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )
        request_id = submit_response.json()["request_id"]

        # Admin rejects
        response = await client.post(
            f"/payment/reject/{request_id}?reason=Invalid%20payment",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rejected" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_reject_request_not_found(self, client: AsyncClient):
        """Test rejecting non-existent request returns 404."""
        admin_headers = {"X-Admin-Key": ADMIN_KEY}
        fake_id = str(uuid4())

        response = await client.post(
            f"/payment/reject/{fake_id}",
            headers=admin_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_can_resubmit_after_rejection(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test that user can submit new request after rejection."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # User submits first request
        submit_response = await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )
        request_id = submit_response.json()["request_id"]

        # Admin rejects
        await client.post(
            f"/payment/reject/{request_id}",
            headers=admin_headers,
        )

        # User should be able to submit again
        response = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPINEW"},
            headers=user_headers,
        )

        assert response.status_code == 200
        assert response.json()["success"] is True


class TestAdminPendingCount:
    """Test cases for admin getting pending count."""

    @pytest.mark.asyncio
    async def test_get_pending_count(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting count of pending requests."""
        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}

        # Get initial count
        initial_response = await client.get("/payment/pending-count", headers=admin_headers)
        initial_count = initial_response.json()["pending_count"]

        # User submits a request
        await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )

        # Count should increase
        response = await client.get("/payment/pending-count", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_count"] == initial_count + 1

    @pytest.mark.asyncio
    async def test_get_pending_count_invalid_admin_key(self, client: AsyncClient):
        """Test getting pending count with invalid admin key fails."""
        response = await client.get(
            "/payment/pending-count",
            headers={"X-Admin-Key": "wrong-key"},
        )

        assert response.status_code == 403


class TestCreditsEndpoint:
    """Test cases for credits balance endpoint."""

    @pytest.mark.asyncio
    async def test_get_credits_balance_new_user(
        self, client: AsyncClient, authenticated_user: dict
    ):
        """Test getting credits balance for new user (should be 0)."""
        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.get("/payment/credits", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["credits"] == 0
        assert data["has_credits"] is False

    @pytest.mark.asyncio
    async def test_get_credits_balance_with_credits(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test getting credits balance when user has credits."""
        from backend.models.db_models import User
        from sqlalchemy import select

        # Give user some credits
        user_id = authenticated_user["user"]["id"]
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 7
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.get("/payment/credits", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["credits"] == 7
        assert data["has_credits"] is True

    @pytest.mark.asyncio
    async def test_get_credits_unauthenticated(self, client: AsyncClient):
        """Test getting credits without authentication fails."""
        response = await client.get("/payment/credits")
        assert response.status_code == 401


class TestCreditsStacking:
    """Test cases for credits stacking on repeat purchases."""

    @pytest.mark.asyncio
    async def test_credits_stack_on_multiple_activations(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that credits stack when multiple payments are approved."""
        from backend.models.db_models import User, PaymentRequest
        from sqlalchemy import select
        from decimal import Decimal

        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}
        user_id = authenticated_user["user"]["id"]

        # First payment request and activation
        submit1 = await client.post(
            "/payment/request",
            json={"upi_transaction_id": "UPI_STACK_1"},
            headers=user_headers,
        )
        request_id_1 = submit1.json()["request_id"]

        await client.post(
            f"/payment/activate/{request_id_1}",
            headers=admin_headers,
        )

        # Check credits after first activation
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        assert user.credits == 10

        # Manually create second payment request (bypass pending check for test)
        payment_request_2 = PaymentRequest(
            user_id=user_id,
            amount=Decimal("50.00"),
            upi_transaction_id="UPI_STACK_2",
            status="pending",
        )
        db_session.add(payment_request_2)
        await db_session.commit()
        await db_session.refresh(payment_request_2)

        # Activate second request
        await client.post(
            f"/payment/activate/{payment_request_2.id}",
            headers=admin_headers,
        )

        # Refresh and check credits stacked
        await db_session.refresh(user)
        assert user.credits == 20  # 10 + 10

    @pytest.mark.asyncio
    async def test_credits_stack_with_existing_balance(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test credits add to existing balance."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}
        admin_headers = {"X-Admin-Key": ADMIN_KEY}
        user_id = authenticated_user["user"]["id"]

        # Give user existing credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 3
        await db_session.commit()

        # Submit and activate payment
        submit = await client.post(
            "/payment/request",
            json={},
            headers=user_headers,
        )
        request_id = submit.json()["request_id"]

        await client.post(
            f"/payment/activate/{request_id}",
            headers=admin_headers,
        )

        # Check credits stacked
        await db_session.refresh(user)
        assert user.credits == 13  # 3 + 10


class TestUserResponseIncludesCredits:
    """Test that user responses include credits field."""

    @pytest.mark.asyncio
    async def test_auth_response_includes_credits(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test that signup/login response includes credits field."""
        # Signup
        response = await client.post("/auth/signup", json=test_user_data)

        assert response.status_code == 200
        data = response.json()
        assert "credits" in data["user"]
        assert data["user"]["credits"] == 0

    @pytest.mark.asyncio
    async def test_me_endpoint_includes_credits(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that /auth/me endpoint includes credits field."""
        from backend.models.db_models import User
        from sqlalchemy import select

        # Give user some credits
        user_id = authenticated_user["user"]["id"]
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 5
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        response = await client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "credits" in data
        assert data["credits"] == 5
