"""
Authentication service handling user signup, login, and token management.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.security import (
    hash_password,
    verify_password,
    hash_token,
    create_token_pair,
    create_access_token,
    decode_refresh_token,
    get_token_expiry,
    TokenPair,
)
from backend.models.db_models import User, RefreshToken, UserState


class AuthService:
    """Service class for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== User Operations =====

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, 
        email: str, 
        password: str, 
        full_name: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Create a new user account.
        Returns (user, error_message).
        """
        # Check if email already exists
        existing = await self.get_user_by_email(email)
        if existing:
            return None, "Email already registered"

        # Create user
        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()  # Get the user ID

        # Create initial user state
        user_state = UserState(user_id=user.id)
        self.db.add(user_state)

        return user, None

    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        Returns user if valid, None if invalid credentials.
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)

    # ===== Token Operations =====

    async def create_tokens(
        self, 
        user: User,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenPair:
        """
        Create access and refresh token pair for user.
        Also stores refresh token hash in database.
        """
        # Create token pair
        tokens = create_token_pair(user.id, user.email)

        # Enforce session limit - delete oldest if at max
        await self._enforce_session_limit(user.id)

        # Store refresh token hash in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(tokens.refresh_token),
            device_info=device_info,
            ip_address=ip_address,
            expires_at=get_token_expiry("refresh"),
        )
        self.db.add(refresh_token_record)

        return tokens

    async def refresh_access_token(
        self, 
        refresh_token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Tuple[Optional[TokenPair], Optional[str]]:
        """
        Refresh access token using refresh token.
        Returns (new_tokens, error_message).
        """
        # Decode and validate refresh token
        token_data = decode_refresh_token(refresh_token)
        if not token_data:
            return None, "Invalid refresh token"

        # Check if refresh token exists in database
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            return None, "Refresh token not found or revoked"

        # Check if token is expired
        if stored_token.expires_at < datetime.now(timezone.utc):
            # Delete expired token
            await self.db.delete(stored_token)
            return None, "Refresh token expired"

        # Get user
        user = await self.get_user_by_id(token_data.user_id)
        if not user or not user.is_active:
            return None, "User not found or inactive"

        # Delete old refresh token (rotation)
        await self.db.delete(stored_token)

        # Create new token pair
        tokens = await self.create_tokens(user, device_info, ip_address)

        # Update last used
        await self.update_last_login(user.id)

        return tokens, None

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a specific refresh token (logout from one device).
        Returns True if token was found and revoked.
        """
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.rowcount > 0

    async def revoke_all_refresh_tokens(self, user_id: UUID) -> int:
        """
        Revoke all refresh tokens for a user (logout from all devices).
        Returns number of tokens revoked.
        """
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return result.rowcount

    async def _enforce_session_limit(self, user_id: UUID) -> None:
        """Delete oldest sessions if user exceeds max session limit."""
        # Count current sessions
        result = await self.db.execute(
            select(func.count()).where(RefreshToken.user_id == user_id)
        )
        count = result.scalar()

        if count >= settings.max_sessions_per_user:
            # Get oldest tokens to delete
            tokens_to_delete = settings.max_sessions_per_user - count + 1
            if tokens_to_delete > 0:
                oldest_tokens = await self.db.execute(
                    select(RefreshToken.id)
                    .where(RefreshToken.user_id == user_id)
                    .order_by(RefreshToken.created_at.asc())
                    .limit(tokens_to_delete)
                )
                token_ids = [row[0] for row in oldest_tokens.fetchall()]
                if token_ids:
                    await self.db.execute(
                        delete(RefreshToken).where(RefreshToken.id.in_(token_ids))
                    )

    # ===== Session Management =====

    async def get_active_sessions(self, user_id: UUID) -> list:
        """Get all active sessions for a user."""
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.expires_at > datetime.now(timezone.utc))
            .order_by(RefreshToken.last_used_at.desc())
        )
        return list(result.scalars().all())

    async def cleanup_expired_tokens(self) -> int:
        """Remove all expired refresh tokens. Run periodically."""
        result = await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        return result.rowcount

