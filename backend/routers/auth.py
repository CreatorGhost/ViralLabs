"""
Authentication router handling signup, login, logout, and token refresh.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user, get_client_info
from backend.models.db_models import User
from backend.models.schemas import (
    SignupRequest,
    LoginRequest,
    RefreshTokenRequest,
    AuthResponse,
    UserResponse,
    TokenResponse,
    ActiveSessionsResponse,
    SessionInfo,
)
from backend.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    client_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    Returns access and refresh tokens on successful registration.
    """
    auth_service = AuthService(db)
    client_info = get_client_info(client_request)
    
    # Create user
    user, error = await auth_service.create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    
    if error:
        return AuthResponse(success=False, error=error)
    
    # Create tokens
    tokens = await auth_service.create_tokens(
        user,
        device_info=client_info["device_info"],
        ip_address=client_info["ip_address"],
    )
    
    return AuthResponse(
        success=True,
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    client_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return tokens.
    
    Returns access and refresh tokens on successful login.
    """
    auth_service = AuthService(db)
    client_info = get_client_info(client_request)
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        email=request.email,
        password=request.password,
    )
    
    if not user:
        return AuthResponse(success=False, error="Invalid email or password")
    
    # Update last login and create tokens
    await auth_service.update_last_login(user.id)
    tokens = await auth_service.create_tokens(
        user,
        device_info=client_info["device_info"],
        ip_address=client_info["ip_address"],
    )
    
    return AuthResponse(
        success=True,
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
        ),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    client_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Returns new access and refresh tokens (token rotation).
    """
    auth_service = AuthService(db)
    client_info = get_client_info(client_request)
    
    tokens, error = await auth_service.refresh_access_token(
        refresh_token=request.refresh_token,
        device_info=client_info["device_info"],
        ip_address=client_info["ip_address"],
    )
    
    if error:
        return AuthResponse(success=False, error=error)
    
    return AuthResponse(
        success=True,
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
        ),
    )


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from current device by revoking the refresh token.
    """
    auth_service = AuthService(db)
    revoked = await auth_service.revoke_refresh_token(request.refresh_token)
    
    return {
        "success": True,
        "message": "Logged out successfully" if revoked else "Token already revoked or invalid",
    }


@router.post("/logout-all")
async def logout_all(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from all devices by revoking all refresh tokens.
    Requires authentication.
    """
    auth_service = AuthService(db)
    count = await auth_service.revoke_all_refresh_tokens(user.id)
    
    return {
        "success": True,
        "message": f"Logged out from {count} device(s)",
        "sessions_revoked": count,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's information.
    """
    return UserResponse.model_validate(user)


@router.get("/sessions", response_model=ActiveSessionsResponse)
async def get_active_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of active sessions for the current user.
    """
    auth_service = AuthService(db)
    sessions = await auth_service.get_active_sessions(user.id)
    
    return ActiveSessionsResponse(
        sessions=[SessionInfo.model_validate(s) for s in sessions],
        count=len(sessions),
    )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session by its ID.
    """
    from uuid import UUID
    from sqlalchemy import delete
    from backend.models.db_models import RefreshToken
    
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format",
        )
    
    # Delete the session (only if it belongs to the current user)
    result = await db.execute(
        delete(RefreshToken).where(
            RefreshToken.id == session_uuid,
            RefreshToken.user_id == user.id,
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    return {"success": True, "message": "Session revoked"}

