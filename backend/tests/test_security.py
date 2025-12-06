"""
Test cases for security utilities (JWT, password hashing).
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.core.security import (
    hash_password,
    verify_password,
    hash_token,
    generate_refresh_token,
    create_access_token,
    create_refresh_token_jwt,
    create_token_pair,
    decode_token,
    decode_access_token,
    decode_refresh_token,
    is_token_expired,
    get_token_expiry,
)


class TestPasswordHashing:
    """Test cases for password hashing functions."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salting)."""
        password = "testpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        hashed = hash_password("correctpassword")
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_password_empty(self):
        """Test verifying empty password."""
        hashed = hash_password("somepassword")
        
        assert verify_password("", hashed) is False
    
    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters."""
        password = "пароль123密码"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_with_invalid_hash(self):
        """Test verify_password handles invalid hash gracefully."""
        result = verify_password("password", "not-a-valid-hash")
        assert result is False


class TestTokenHashing:
    """Test cases for token hashing functions."""
    
    def test_hash_token_returns_string(self):
        """Test that hash_token returns a string."""
        token = "some-token-value"
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex digest
    
    def test_hash_token_deterministic(self):
        """Test that hash_token is deterministic."""
        token = "some-token-value"
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        
        assert hash1 == hash2
    
    def test_generate_refresh_token(self):
        """Test that generate_refresh_token creates unique tokens."""
        token1 = generate_refresh_token()
        token2 = generate_refresh_token()
        
        assert token1 != token2
        assert len(token1) > 0


class TestJWTTokens:
    """Test cases for JWT token generation and validation."""
    
    def test_create_access_token(self):
        """Test creating an access token."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token_jwt(self):
        """Test creating a refresh token JWT."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_refresh_token_jwt(user_id, email)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_pair(self):
        """Test creating a token pair."""
        user_id = uuid4()
        email = "test@example.com"
        
        pair = create_token_pair(user_id, email)
        
        assert pair.access_token is not None
        assert pair.refresh_token is not None
        assert pair.token_type == "bearer"
        assert pair.expires_in > 0
    
    def test_decode_access_token_valid(self):
        """Test decoding a valid access token."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        token_data = decode_access_token(token)
        
        assert token_data is not None
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.token_type == "access"
    
    def test_decode_refresh_token_valid(self):
        """Test decoding a valid refresh token."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_refresh_token_jwt(user_id, email)
        token_data = decode_refresh_token(token)
        
        assert token_data is not None
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.token_type == "refresh"
    
    def test_decode_access_token_rejects_refresh(self):
        """Test that decode_access_token rejects refresh tokens."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_refresh_token_jwt(user_id, email)
        token_data = decode_access_token(token)
        
        assert token_data is None
    
    def test_decode_refresh_token_rejects_access(self):
        """Test that decode_refresh_token rejects access tokens."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        token_data = decode_refresh_token(token)
        
        assert token_data is None
    
    def test_decode_token_invalid(self):
        """Test decoding invalid token returns None."""
        token_data = decode_token("invalid.token.here")
        
        assert token_data is None
    
    def test_decode_token_malformed(self):
        """Test decoding malformed token returns None."""
        token_data = decode_token("not-even-close-to-jwt")
        
        assert token_data is None
    
    def test_is_token_expired(self):
        """Test checking if token is expired."""
        user_id = uuid4()
        email = "test@example.com"
        
        # Create a valid token
        token = create_access_token(user_id, email)
        token_data = decode_access_token(token)
        
        # Should not be expired
        assert is_token_expired(token_data) is False
    
    def test_get_token_expiry(self):
        """Test getting token expiry datetime."""
        access_expiry = get_token_expiry("access")
        refresh_expiry = get_token_expiry("refresh")
        
        now = datetime.now(timezone.utc)
        
        # Access token should expire within 1 hour
        assert access_expiry > now
        assert access_expiry < now + timedelta(hours=1)
        
        # Refresh token should expire within 30 days
        assert refresh_expiry > now
        assert refresh_expiry < now + timedelta(days=30)
        assert refresh_expiry > access_expiry


class TestTokenIntegrity:
    """Test cases for token integrity and security."""
    
    def test_modified_token_fails_validation(self):
        """Test that modified tokens fail validation."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        
        # Modify the token slightly
        modified_token = token[:-5] + "XXXXX"
        
        token_data = decode_access_token(modified_token)
        assert token_data is None
    
    def test_tokens_contain_correct_claims(self):
        """Test that tokens contain all expected claims."""
        user_id = uuid4()
        email = "test@example.com"
        
        token = create_access_token(user_id, email)
        token_data = decode_token(token)
        
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.token_type == "access"
        assert token_data.exp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

