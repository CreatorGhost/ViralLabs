"""
Session management endpoints.
Single Responsibility: Only handles session state retrieval.
"""

from fastapi import APIRouter

from backend.core.session import session_manager
from backend.models.schemas import SessionState

router = APIRouter(tags=["Session"])


@router.get("/session/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """Get current session state."""
    session = session_manager.get_or_create(session_id)
    return SessionState(
        has_face=session.get("has_face", False),
        face_id=session.get("face_id"),
        face_path=session.get("face_path"),
        last_script=session.get("last_script"),
        last_thumbnails=session.get("last_thumbnails")
    )


