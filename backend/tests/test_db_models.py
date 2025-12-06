"""
Test cases for database models.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import User, RefreshToken, UserState, MediaFile, Generation
from backend.core.security import hash_password


class TestUserModel:
    """Test cases for User model."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            password_hash=hash_password("testpassword"),
            full_name="Test User",
        )
        db_session.add(user)
        await db_session.flush()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_premium is False
        assert user.is_active is True
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_user_defaults(self, db_session: AsyncSession):
        """Test user default values."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        assert user.is_premium is False
        assert user.is_active is True
        assert user.premium_expires_at is None
        assert user.last_login is None


class TestRefreshTokenModel:
    """Test cases for RefreshToken model."""
    
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, db_session: AsyncSession):
        """Test creating a refresh token."""
        # First create a user
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        # Create refresh token
        token = RefreshToken(
            user_id=user.id,
            token_hash="token_hash_value",
            device_info="Test Device",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc),
        )
        db_session.add(token)
        await db_session.flush()
        
        assert token.id is not None
        assert token.user_id == user.id
        assert token.token_hash == "token_hash_value"
    
    @pytest.mark.asyncio
    async def test_refresh_token_cascade_delete(self, db_session: AsyncSession):
        """Test that refresh tokens are deleted when user is deleted."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        token = RefreshToken(
            user_id=user.id,
            token_hash="token_hash",
            expires_at=datetime.now(timezone.utc),
        )
        db_session.add(token)
        await db_session.flush()
        
        token_id = token.id
        
        # Delete user
        await db_session.delete(user)
        await db_session.flush()
        
        # Token should be deleted (cascade)
        result = await db_session.get(RefreshToken, token_id)
        assert result is None


class TestUserStateModel:
    """Test cases for UserState model."""
    
    @pytest.mark.asyncio
    async def test_create_user_state(self, db_session: AsyncSession):
        """Test creating user state."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        state = UserState(user_id=user.id)
        db_session.add(state)
        await db_session.flush()
        
        assert state.id is not None
        assert state.user_id == user.id
        assert state.current_face_id is None
        assert state.preferences == {}
    
    @pytest.mark.asyncio
    async def test_user_state_preferences_json(self, db_session: AsyncSession):
        """Test that preferences can store JSON data."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        preferences = {
            "theme": "dark",
            "language": "en",
            "notifications": True,
        }
        
        state = UserState(
            user_id=user.id,
            preferences=preferences,
        )
        db_session.add(state)
        await db_session.flush()
        
        assert state.preferences["theme"] == "dark"
        assert state.preferences["notifications"] is True


class TestMediaFileModel:
    """Test cases for MediaFile model."""
    
    @pytest.mark.asyncio
    async def test_create_media_file(self, db_session: AsyncSession):
        """Test creating a media file."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        media = MediaFile(
            user_id=user.id,
            file_type="thumbnail",
            storage_key="/path/to/file.png",
            original_filename="thumbnail.png",
            file_size=12345,
            mime_type="image/png",
        )
        db_session.add(media)
        await db_session.flush()
        
        assert media.id is not None
        assert media.file_type == "thumbnail"
        assert media.storage_type == "local"  # Default
        assert media.file_size == 12345
    
    @pytest.mark.asyncio
    async def test_media_file_metadata(self, db_session: AsyncSession):
        """Test media file metadata storage."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        metadata = {
            "width": 1920,
            "height": 1080,
            "format": "png",
        }
        
        media = MediaFile(
            user_id=user.id,
            file_type="thumbnail",
            storage_key="/path/to/file.png",
            file_metadata=metadata,
        )
        db_session.add(media)
        await db_session.flush()
        
        assert media.file_metadata["width"] == 1920
        assert media.file_metadata["height"] == 1080


class TestGenerationModel:
    """Test cases for Generation model."""
    
    @pytest.mark.asyncio
    async def test_create_generation(self, db_session: AsyncSession):
        """Test creating a generation record."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        generation = Generation(
            user_id=user.id,
            generation_type="script",
            topic="Python tutorial",
            input_settings={"model": "gpt-4", "temperature": 0.7},
            output_data={"script": "Hello world..."},
            status="completed",
        )
        db_session.add(generation)
        await db_session.flush()
        
        assert generation.id is not None
        assert generation.generation_type == "script"
        assert generation.topic == "Python tutorial"
        assert generation.status == "completed"
    
    @pytest.mark.asyncio
    async def test_generation_parent_relationship(self, db_session: AsyncSession):
        """Test generation parent-child relationship."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        # Create parent generation (script)
        parent = Generation(
            user_id=user.id,
            generation_type="script",
            topic="Python tutorial",
        )
        db_session.add(parent)
        await db_session.flush()
        
        # Create child generation (audio from script)
        child = Generation(
            user_id=user.id,
            generation_type="audio",
            topic="Python tutorial",
            parent_generation_id=parent.id,
        )
        db_session.add(child)
        await db_session.flush()
        
        assert child.parent_generation_id == parent.id
    
    @pytest.mark.asyncio
    async def test_generation_status_values(self, db_session: AsyncSession):
        """Test generation with different status values."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test",
        )
        db_session.add(user)
        await db_session.flush()
        
        for status in ["pending", "processing", "completed", "failed"]:
            gen = Generation(
                user_id=user.id,
                generation_type="script",
                status=status,
            )
            db_session.add(gen)
            await db_session.flush()
            
            assert gen.status == status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

