"""
Test cases for authentication endpoints.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestSignup:
    """Test cases for user signup endpoint."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user signup."""
        response = await client.post("/auth/signup", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["user"]["email"] == test_user_data["email"].lower()
        assert data["user"]["full_name"] == test_user_data["full_name"]
        assert data["user"]["is_premium"] is False
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"
        assert data["tokens"]["expires_in"] > 0
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        """Test signup with duplicate email returns error."""
        # First signup
        await client.post("/auth/signup", json=test_user_data)
        
        # Second signup with same email
        response = await client.post("/auth/signup", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "already registered" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_signup_invalid_email(self, client: AsyncClient):
        """Test signup with invalid email format."""
        response = await client.post("/auth/signup", json={
            "email": "not-an-email",
            "password": "testpassword123",
            "full_name": "Test User"
        })
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_signup_short_password(self, client: AsyncClient):
        """Test signup with password too short."""
        response = await client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "short",  # Less than 8 chars
            "full_name": "Test User"
        })
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_signup_missing_fields(self, client: AsyncClient):
        """Test signup with missing required fields."""
        # Missing password
        response = await client.post("/auth/signup", json={
            "email": "test@example.com",
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Missing email
        response = await client.post("/auth/signup", json={
            "password": "testpassword123",
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Missing full_name
        response = await client.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        assert response.status_code == 422


class TestLogin:
    """Test cases for user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful login."""
        # First create user
        await client.post("/auth/signup", json=test_user_data)
        
        # Then login
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["user"]["email"] == test_user_data["email"].lower()
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data: dict):
        """Test login with wrong password."""
        await client.post("/auth/signup", json=test_user_data)
        
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "invalid" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "invalid" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user_data: dict):
        """Test that email login is case insensitive."""
        await client.post("/auth/signup", json=test_user_data)
        
        # Login with uppercase email
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"].upper(),
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTokenRefresh:
    """Test cases for token refresh endpoint."""
    
    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful token refresh."""
        # Signup and get tokens
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        # Small delay to ensure different timestamp in JWT
        import asyncio
        await asyncio.sleep(1.1)
        
        # Refresh token
        response = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "tokens" in data
        assert data["tokens"]["token_type"] == "bearer"
        assert data["tokens"]["expires_in"] > 0
    
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post("/auth/refresh", json={
            "refresh_token": "invalid.token.here"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "invalid" in data["error"].lower()
    
    @pytest.mark.asyncio
    async def test_refresh_token_rotation(self, client: AsyncClient, test_user_data: dict):
        """Test that refresh creates new tokens and old token hash is deleted."""
        # Signup and get tokens
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        # First refresh - should succeed and return new tokens
        response1 = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        data1 = response1.json()
        assert data1["success"] is True
        new_refresh_token = data1["tokens"]["refresh_token"]
        
        # Using new refresh token should work
        response2 = await client.post("/auth/refresh", json={
            "refresh_token": new_refresh_token
        })
        assert response2.json()["success"] is True


class TestLogout:
    """Test cases for logout endpoints."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful logout."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        response = await client.post("/auth/logout", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_logout_invalidates_refresh_token(self, client: AsyncClient, test_user_data: dict):
        """Test that logout invalidates the refresh token."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        # Logout
        await client.post("/auth/logout", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        # Try to use the refresh token
        response = await client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.asyncio
    async def test_logout_all_sessions(self, client: AsyncClient, test_user_data: dict):
        """Test logout from all devices."""
        # Signup and get initial tokens
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        # Login again to create another session
        login_response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        tokens2 = login_response.json()["tokens"]
        
        # Logout all using first token
        response = await client.post(
            "/auth/logout-all",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["sessions_revoked"] >= 2


class TestProtectedEndpoints:
    """Test cases for protected endpoints requiring authentication."""
    
    @pytest.mark.asyncio
    async def test_me_endpoint_authenticated(self, client: AsyncClient, test_user_data: dict):
        """Test /auth/me endpoint with valid token."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"].lower()
        assert data["full_name"] == test_user_data["full_name"]
    
    @pytest.mark.asyncio
    async def test_me_endpoint_no_auth(self, client: AsyncClient):
        """Test /auth/me endpoint without token."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_me_endpoint_invalid_token(self, client: AsyncClient):
        """Test /auth/me endpoint with invalid token."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_sessions_endpoint(self, client: AsyncClient, test_user_data: dict):
        """Test /auth/sessions endpoint."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        response = await client.get(
            "/auth/sessions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "count" in data
        assert data["count"] >= 1


class TestSessionLimit:
    """Test cases for session limit enforcement."""
    
    @pytest.mark.asyncio
    async def test_max_sessions_enforced(self, client: AsyncClient, test_user_data: dict):
        """Test that max sessions per user is enforced."""
        # Signup
        await client.post("/auth/signup", json=test_user_data)
        
        # Login multiple times to create many sessions
        for _ in range(6):  # Max is 5, so 6th should trigger cleanup
            await client.post("/auth/login", json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
        
        # Get latest token
        login_response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        tokens = login_response.json()["tokens"]
        
        # Check sessions count
        response = await client.get(
            "/auth/sessions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        data = response.json()
        # Should be capped at max_sessions_per_user (5)
        assert data["count"] <= 5


class TestRevokeSessions:
    """Test cases for revoking specific sessions."""
    
    @pytest.mark.asyncio
    async def test_revoke_specific_session(self, client: AsyncClient, test_user_data: dict):
        """Test revoking a specific session by ID."""
        # Signup
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        # Get sessions
        sessions_response = await client.get(
            "/auth/sessions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        sessions = sessions_response.json()["sessions"]
        session_id = sessions[0]["id"]
        
        # Revoke session
        response = await client.delete(
            f"/auth/sessions/{session_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_revoke_invalid_session_id(self, client: AsyncClient, test_user_data: dict):
        """Test revoking with invalid session ID format."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        response = await client.delete(
            "/auth/sessions/invalid-id",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_revoke_nonexistent_session(self, client: AsyncClient, test_user_data: dict):
        """Test revoking non-existent session."""
        signup_response = await client.post("/auth/signup", json=test_user_data)
        tokens = signup_response.json()["tokens"]
        
        fake_uuid = str(uuid4())
        response = await client.delete(
            f"/auth/sessions/{fake_uuid}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

