"""
User service for user-related operations beyond authentication.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import User, UserState, MediaFile


class UserService:
    """Service class for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== User Profile =====

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user_profile(
        self, 
        user_id: UUID, 
        full_name: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if full_name is not None:
            user.full_name = full_name
        user.updated_at = datetime.now(timezone.utc)
        
        return user

    # ===== User State =====

    async def get_user_state(self, user_id: UUID) -> Optional[UserState]:
        """Get user state (preferences, current face, etc.)."""
        result = await self.db.execute(
            select(UserState).where(UserState.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_user_state(self, user_id: UUID) -> UserState:
        """Get user state or create if doesn't exist."""
        state = await self.get_user_state(user_id)
        if not state:
            state = UserState(user_id=user_id)
            self.db.add(state)
            await self.db.flush()
        return state

    async def update_user_state(
        self, 
        user_id: UUID,
        current_face_id: Optional[UUID] = None,
        preferences: Optional[dict] = None,
    ) -> UserState:
        """Update user state."""
        state = await self.get_or_create_user_state(user_id)
        
        if current_face_id is not None:
            state.current_face_id = current_face_id
        if preferences is not None:
            state.preferences = {**state.preferences, **preferences}
        state.updated_at = datetime.now(timezone.utc)
        
        return state

    async def set_current_face(self, user_id: UUID, face_id: Optional[UUID]) -> UserState:
        """Set the current face for a user."""
        return await self.update_user_state(user_id, current_face_id=face_id)

    async def get_current_face(self, user_id: UUID) -> Optional[MediaFile]:
        """Get the current face file for a user."""
        state = await self.get_user_state(user_id)
        if not state or not state.current_face_id:
            return None
        
        result = await self.db.execute(
            select(MediaFile).where(MediaFile.id == state.current_face_id)
        )
        return result.scalar_one_or_none()

    # ===== Subscription =====

    async def update_premium_status(
        self, 
        user_id: UUID, 
        is_premium: bool,
        expires_at: Optional[datetime] = None,
    ) -> Optional[User]:
        """Update user's premium subscription status."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_premium = is_premium
        user.premium_expires_at = expires_at
        user.updated_at = datetime.now(timezone.utc)
        
        return user

    async def check_premium_status(self, user_id: UUID) -> bool:
        """Check if user has active premium subscription."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not user.is_premium:
            return False
        
        # Check if premium has expired
        if user.premium_expires_at and user.premium_expires_at < datetime.now(timezone.utc):
            # Auto-disable expired premium
            user.is_premium = False
            return False
        
        return True

