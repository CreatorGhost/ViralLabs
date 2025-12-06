"""
Session management for user state.
Single Responsibility: Only handles session storage and retrieval.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List


class SessionManager:
    """
    Manages user sessions with in-memory storage.
    In production, this could be swapped for Redis or database storage.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create(self, session_id: str) -> Dict[str, Any]:
        """Get existing session or create a new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "has_face": False,
                "face_id": None,
                "face_path": None,
                "last_script": None,
                "last_thumbnails": None,
                "research_data": None
            }
        return self._sessions[session_id]
    
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session if it exists."""
        return self._sessions.get(session_id)
    
    def update(self, session_id: str, data: Dict[str, Any]) -> None:
        """Update session with new data."""
        session = self.get_or_create(session_id)
        session.update(data)
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_face_path(self, session_id: str) -> Optional[Path]:
        """Get the face image path for a session."""
        session = self.get_or_create(session_id)
        face_path = session.get("face_path")
        if face_path and Path(face_path).exists():
            return Path(face_path)
        return None
    
    def set_face(self, session_id: str, face_id: str, face_path: str) -> None:
        """Set face information for a session."""
        session = self.get_or_create(session_id)
        session["has_face"] = True
        session["face_id"] = face_id
        session["face_path"] = face_path
    
    def clear_face(self, session_id: str) -> Optional[str]:
        """Clear face from session and return old path for cleanup."""
        session = self.get_or_create(session_id)
        old_path = session.get("face_path")
        session["has_face"] = False
        session["face_id"] = None
        session["face_path"] = None
        return old_path
    
    def set_last_script(self, session_id: str, script_data: Dict[str, Any]) -> None:
        """Store last generated script."""
        session = self.get_or_create(session_id)
        session["last_script"] = script_data
    
    def set_research_data(self, session_id: str, research_data: Dict[str, Any]) -> None:
        """Store research data for regeneration."""
        session = self.get_or_create(session_id)
        session["research_data"] = research_data
    
    def set_last_thumbnails(self, session_id: str, thumbnails: List[Dict]) -> None:
        """Store last generated thumbnails."""
        session = self.get_or_create(session_id)
        session["last_thumbnails"] = thumbnails
    
    def set_data(self, session_id: str, key: str, value: Any) -> None:
        """Store arbitrary data in session."""
        session = self.get_or_create(session_id)
        session[key] = value
    
    def get_data(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get arbitrary data from session."""
        session = self.get_or_create(session_id)
        return session.get(key, default)


# Global session manager instance
session_manager = SessionManager()

