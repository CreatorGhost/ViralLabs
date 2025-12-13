"""
Session management endpoints.
Single Responsibility: Only handles session state retrieval.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.db_models import User, MediaFile, UserState
from backend.models.schemas import SessionState

router = APIRouter(tags=["Session"])


@router.get("/session/{session_id}", response_model=SessionState)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current session state from database."""
    
    # Get user's face from database
    face_query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "face"
    ).order_by(MediaFile.created_at.desc())
    
    result = await db.execute(face_query)
    face = result.scalar_one_or_none()
    
    has_face = face is not None
    face_id = None
    face_path = None
    
    if face:
        # Get face_id from metadata if stored, otherwise use file ID
        face_id = face.file_metadata.get("face_id") if face.file_metadata else str(face.id)
        face_path = face.storage_url
    
    return SessionState(
        has_face=has_face,
        face_id=face_id,
        face_path=face_path,
        last_script=None,  # TODO: Could add last script from DB if needed
        last_thumbnails=None  # TODO: Could add last thumbnails from DB if needed
    )





