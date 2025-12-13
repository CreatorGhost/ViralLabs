"""Core module for configuration and session management."""

from .config import settings, BASE_DIR, USER_DATA_DIR, FACE_DIR, THUMBNAILS_DIR, FRONTEND_DIR
from .session import SessionManager, session_manager

__all__ = [
    "settings",
    "BASE_DIR",
    "USER_DATA_DIR", 
    "FACE_DIR",
    "THUMBNAILS_DIR",
    "FRONTEND_DIR",
    "SessionManager",
    "session_manager"
]







