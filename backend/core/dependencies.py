"""
FastAPI dependencies for authentication and database access.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import decode_access_token, TokenData
from backend.models.db_models import User
from backend.services.auth_service import AuthService


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that extracts and validates the JWT token,
    returning the current authenticated user.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency that optionally extracts the current user.
    Returns None if not authenticated (doesn't raise exception).
    
    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if not token_data:
        return None
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    if not user or not user.is_active:
        return None
    
    return user


async def get_premium_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires user to have premium subscription.
    
    Usage:
        @app.get("/premium-feature")
        async def premium_feature(user: User = Depends(get_premium_user)):
            return {"feature": "premium content"}
    """
    if not user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required",
        )
    return user


def get_client_info(request: Request) -> dict:
    """
    Extract client information from request for session tracking.
    """
    return {
        "ip_address": request.client.host if request.client else None,
        "device_info": request.headers.get("User-Agent", "Unknown"),
    }

