"""
Security utilities for authentication.
Handles JWT token generation/validation and password hashing.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.core.config import settings


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: UUID
    email: str
    token_type: str  # "access" or "refresh"
    exp: datetime


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds


# ===== Password Hashing =====

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Encode password to bytes and generate salt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ===== Token Hashing (for refresh tokens stored in DB) =====

def hash_token(token: str) -> str:
    """
    Hash a refresh token for secure storage.
    Uses SHA-256 since we don't need bcrypt's slowness for token comparison.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_refresh_token() -> str:
    """Generate a cryptographically secure refresh token."""
    return secrets.token_urlsafe(64)


# ===== JWT Token Generation =====

def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create a short-lived JWT access token.
    Contains user_id and email for authorization.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token_jwt(user_id: UUID, email: str) -> str:
    """
    Create a long-lived JWT refresh token.
    Used to obtain new access tokens.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_token_pair(user_id: UUID, email: str) -> TokenPair:
    """Create both access and refresh tokens."""
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token_jwt(user_id, email)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
    )


# ===== JWT Token Validation =====

def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    Returns TokenData if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("type")
        exp = payload.get("exp")
        
        if not all([user_id, email, token_type, exp]):
            return None
        
        return TokenData(
            user_id=UUID(user_id),
            email=email,
            token_type=token_type,
            exp=datetime.fromtimestamp(exp, tz=timezone.utc),
        )
    except JWTError:
        return None


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate an access token specifically."""
    token_data = decode_token(token)
    if token_data and token_data.token_type == "access":
        return token_data
    return None


def decode_refresh_token(token: str) -> Optional[TokenData]:
    """Decode and validate a refresh token specifically."""
    token_data = decode_token(token)
    if token_data and token_data.token_type == "refresh":
        return token_data
    return None


def is_token_expired(token_data: TokenData) -> bool:
    """Check if a token has expired."""
    return datetime.now(timezone.utc) > token_data.exp


# ===== Utility Functions =====

def get_token_expiry(token_type: str = "access") -> datetime:
    """Get the expiry datetime for a new token."""
    if token_type == "refresh":
        return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

