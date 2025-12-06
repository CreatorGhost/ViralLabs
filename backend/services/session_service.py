"""
Database-backed session service for authenticated users.
Provides persistent state management across sessions.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db_models import UserState, MediaFile, Generation


class DatabaseSessionService:
    """
    Database-backed session service for authenticated users.
    Replaces in-memory SessionManager for persistent storage.
    """

    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id

    async def get_or_create_state(self) -> UserState:
        """Get user state or create if doesn't exist."""
        result = await self.db.execute(
            select(UserState).where(UserState.user_id == self.user_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            state = UserState(user_id=self.user_id)
            self.db.add(state)
            await self.db.flush()
        
        return state

    async def get_state(self) -> Optional[UserState]:
        """Get user state if exists."""
        result = await self.db.execute(
            select(UserState).where(UserState.user_id == self.user_id)
        )
        return result.scalar_one_or_none()

    # ===== Face Management =====

    async def get_face_path(self) -> Optional[Path]:
        """Get the face image path for the user."""
        state = await self.get_state()
        if not state or not state.current_face_id:
            return None
        
        # Get the media file
        result = await self.db.execute(
            select(MediaFile).where(MediaFile.id == state.current_face_id)
        )
        media = result.scalar_one_or_none()
        
        if media and Path(media.storage_key).exists():
            return Path(media.storage_key)
        return None

    async def get_current_face(self) -> Optional[MediaFile]:
        """Get the current face MediaFile."""
        state = await self.get_state()
        if not state or not state.current_face_id:
            return None
        
        result = await self.db.execute(
            select(MediaFile).where(MediaFile.id == state.current_face_id)
        )
        return result.scalar_one_or_none()

    async def set_face(
        self, 
        face_path: str, 
        original_filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> MediaFile:
        """Set face information for the user."""
        # Create media file record
        media_file = MediaFile(
            user_id=self.user_id,
            file_type="face",
            storage_type="local",
            storage_key=face_path,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=mime_type,
        )
        self.db.add(media_file)
        await self.db.flush()
        
        # Update user state
        state = await self.get_or_create_state()
        state.current_face_id = media_file.id
        state.updated_at = datetime.now(timezone.utc)
        
        return media_file

    async def clear_face(self) -> Optional[str]:
        """Clear face from user state and return old path for cleanup."""
        state = await self.get_state()
        if not state or not state.current_face_id:
            return None
        
        # Get old face path
        result = await self.db.execute(
            select(MediaFile).where(MediaFile.id == state.current_face_id)
        )
        old_media = result.scalar_one_or_none()
        old_path = old_media.storage_key if old_media else None
        
        # Clear face reference
        state.current_face_id = None
        state.updated_at = datetime.now(timezone.utc)
        
        # Optionally delete the media record
        if old_media:
            await self.db.delete(old_media)
        
        return old_path

    # ===== Preferences =====

    async def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        state = await self.get_or_create_state()
        return state.preferences or {}

    async def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences (merge with existing)."""
        state = await self.get_or_create_state()
        state.preferences = {**(state.preferences or {}), **preferences}
        state.updated_at = datetime.now(timezone.utc)

    async def set_preference(self, key: str, value: Any) -> None:
        """Set a single preference."""
        await self.update_preferences({key: value})

    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a single preference."""
        prefs = await self.get_preferences()
        return prefs.get(key, default)

    # ===== Generation History =====

    async def save_generation(
        self,
        generation_type: str,
        topic: Optional[str] = None,
        input_settings: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        related_media_ids: Optional[List[UUID]] = None,
        parent_generation_id: Optional[UUID] = None,
        status: str = "completed",
    ) -> Generation:
        """Save a new generation to history."""
        generation = Generation(
            user_id=self.user_id,
            generation_type=generation_type,
            topic=topic,
            input_settings=input_settings or {},
            output_data=output_data or {},
            related_media_ids=related_media_ids,
            parent_generation_id=parent_generation_id,
            status=status,
        )
        self.db.add(generation)
        await self.db.flush()
        return generation

    async def get_last_generation(self, generation_type: str) -> Optional[Generation]:
        """Get the most recent generation of a specific type."""
        result = await self.db.execute(
            select(Generation)
            .where(Generation.user_id == self.user_id)
            .where(Generation.generation_type == generation_type)
            .order_by(Generation.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_generation_history(
        self, 
        generation_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Generation]:
        """Get generation history for the user."""
        query = select(Generation).where(Generation.user_id == self.user_id)
        
        if generation_type:
            query = query.where(Generation.generation_type == generation_type)
        
        query = query.order_by(Generation.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ===== Media Files =====

    async def save_media_file(
        self,
        file_type: str,
        storage_key: str,
        original_filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> MediaFile:
        """Save a media file record."""
        media = MediaFile(
            user_id=self.user_id,
            file_type=file_type,
            storage_type="local",
            storage_key=storage_key,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            file_metadata=metadata or {},
        )
        self.db.add(media)
        await self.db.flush()
        return media

    async def get_media_files(
        self, 
        file_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[MediaFile]:
        """Get media files for the user."""
        query = select(MediaFile).where(MediaFile.user_id == self.user_id)
        
        if file_type:
            query = query.where(MediaFile.file_type == file_type)
        
        query = query.order_by(MediaFile.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ===== Convenience Methods for Last Script/Thumbnails =====

    async def set_last_script(self, script_data: Dict[str, Any], topic: str) -> Generation:
        """Store last generated script."""
        return await self.save_generation(
            generation_type="script",
            topic=topic,
            output_data=script_data,
        )

    async def get_last_script(self) -> Optional[Dict[str, Any]]:
        """Get last generated script data."""
        gen = await self.get_last_generation("script")
        return gen.output_data if gen else None

    async def set_last_thumbnails(
        self, 
        thumbnails: List[Dict], 
        topic: str,
        media_ids: Optional[List[UUID]] = None,
    ) -> Generation:
        """Store last generated thumbnails."""
        return await self.save_generation(
            generation_type="thumbnail",
            topic=topic,
            output_data={"thumbnails": thumbnails},
            related_media_ids=media_ids,
        )

    async def get_last_thumbnails(self) -> Optional[List[Dict]]:
        """Get last generated thumbnails."""
        gen = await self.get_last_generation("thumbnail")
        return gen.output_data.get("thumbnails") if gen else None

